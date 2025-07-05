from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
)
from typing import Optional
import time
import psutil
import os
import threading

# Récupérer l'ID d'instance depuis les variables d'environnement
INSTANCE_ID = os.getenv("INSTANCE_ID", "inventory-api-1")

# Métriques principales avec instance_id
REQUEST_COUNT = Counter(
    "inventory_api_requests_total",
    "Total API requests",
    ["method", "endpoint", "status_code", "instance_id"],
)

REQUEST_DURATION = Histogram(
    "inventory_api_request_duration_seconds",
    "API request duration in seconds",
    ["method", "endpoint", "instance_id"],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

ACTIVE_REQUESTS = Gauge(
    "inventory_api_active_requests", "Number of active requests", ["instance_id"]
)

# Métriques temps réel (non cumulatives)
CURRENT_RPS = Gauge(
    "inventory_api_current_rps", "Current requests per second", ["instance_id"]
)

ERROR_COUNT = Counter(
    "inventory_api_errors_total",
    "Total API errors",
    ["error_type", "endpoint", "instance_id"],
)

HEALTH_STATUS = Gauge(
    "inventory_api_health_status",
    "API health status (1=healthy, 0=unhealthy)",
    ["instance_id"],
)

CPU_USAGE = Gauge(
    "inventory_api_cpu_usage_percent", "CPU usage percentage", ["instance_id"]
)

MEMORY_USAGE = Gauge(
    "inventory_api_memory_usage_bytes", "Memory usage in bytes", ["instance_id"]
)

MEMORY_USAGE_PERCENT = Gauge(
    "inventory_api_memory_usage_percent", "Memory usage percentage", ["instance_id"]
)

# Métriques spécifiques à l'inventaire
PRODUCT_COUNT = Gauge(
    "inventory_api_products_total", "Total number of products", ["instance_id"]
)

CATEGORY_COUNT = Gauge(
    "inventory_api_categories_total", "Total number of categories", ["instance_id"]
)

STOCK_OPERATIONS = Counter(
    "inventory_api_stock_operations_total",
    "Total stock operations",
    ["operation", "instance_id"],
)

LOW_STOCK_PRODUCTS = Gauge(
    "inventory_api_low_stock_products",
    "Number of products with low stock",
    ["instance_id"],
)


class MetricsService:
    def __init__(self):
        # Initialiser le statut de santé avec l'instance ID
        HEALTH_STATUS.labels(instance_id=INSTANCE_ID).set(1)
        # Obtenir le processus actuel
        self.process = psutil.Process(os.getpid())
        # Initialiser le monitoring CPU
        self.process.cpu_percent()  # Premier appel pour initialiser
        # Variables pour calcul RPS temps réel
        self.last_request_count = 0
        self.last_rps_update = time.time()
        # Démarrer le thread de monitoring
        self._start_monitoring_thread()

    def record_request(
        self, method: str, endpoint: str, status_code: int, duration: float
    ):
        """Enregistre une requête"""
        REQUEST_COUNT.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code,
            instance_id=INSTANCE_ID,
        ).inc()
        REQUEST_DURATION.labels(
            method=method, endpoint=endpoint, instance_id=INSTANCE_ID
        ).observe(duration)
        self._update_current_rps()

    def record_error(self, error_type: str, endpoint: str):
        """Enregistre une erreur"""
        ERROR_COUNT.labels(
            error_type=error_type, endpoint=endpoint, instance_id=INSTANCE_ID
        ).inc()

    def set_health_status(self, is_healthy: bool):
        """Met à jour le statut de santé"""
        HEALTH_STATUS.labels(instance_id=INSTANCE_ID).set(1 if is_healthy else 0)

    def increment_active_requests(self):
        """Incrémente le nombre de requêtes actives"""
        ACTIVE_REQUESTS.labels(instance_id=INSTANCE_ID).inc()

    def decrement_active_requests(self):
        """Décrémente le nombre de requêtes actives"""
        ACTIVE_REQUESTS.labels(instance_id=INSTANCE_ID).dec()

    def record_stock_operation(self, operation: str):
        """Enregistre une opération de stock"""
        STOCK_OPERATIONS.labels(operation=operation, instance_id=INSTANCE_ID).inc()

    def update_product_count(self, count: int):
        """Met à jour le nombre total de produits"""
        PRODUCT_COUNT.labels(instance_id=INSTANCE_ID).set(count)

    def update_category_count(self, count: int):
        """Met à jour le nombre total de catégories"""
        CATEGORY_COUNT.labels(instance_id=INSTANCE_ID).set(count)

    def update_low_stock_products(self, count: int):
        """Met à jour le nombre de produits avec stock faible"""
        LOW_STOCK_PRODUCTS.labels(instance_id=INSTANCE_ID).set(count)

    def _start_monitoring_thread(self):
        """Démarre un thread pour monitorer les métriques système en background"""

        def monitor():
            while True:
                try:
                    # CPU usage
                    cpu_percent = psutil.cpu_percent(interval=1)
                    CPU_USAGE.labels(instance_id=INSTANCE_ID).set(cpu_percent)

                    # Memory usage du processus
                    memory_info = self.process.memory_info()
                    MEMORY_USAGE.labels(instance_id=INSTANCE_ID).set(memory_info.rss)

                    # Memory usage percentage du système global
                    memory_info_system = psutil.virtual_memory()
                    MEMORY_USAGE_PERCENT.labels(instance_id=INSTANCE_ID).set(
                        memory_info_system.percent
                    )

                except Exception as e:
                    # En cas d'erreur, on continue sans crasher
                    print(f"Error updating metrics: {e}")

                time.sleep(5)  # Mise à jour toutes les 5 secondes

        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()

    def _update_current_rps(self):
        """Met à jour le RPS temps réel basé sur les requêtes récentes"""
        now = time.time()

        # Calculer le RPS basé sur toutes les requêtes
        total_requests = sum(
            metric.samples[0].value
            for metric in REQUEST_COUNT.collect()
            for sample in metric.samples
            if sample.labels.get("instance_id") == INSTANCE_ID
        )

        if hasattr(self, "last_rps_update") and (now - self.last_rps_update) >= 1.0:
            rps = (total_requests - self.last_request_count) / (
                now - self.last_rps_update
            )
            CURRENT_RPS.labels(instance_id=INSTANCE_ID).set(max(0, rps))
            self.last_request_count = total_requests
            self.last_rps_update = now

    def get_metrics(self) -> str:
        """Retourne les métriques au format Prometheus"""
        return generate_latest()


# Instance globale du service de métriques
metrics_service = MetricsService()
