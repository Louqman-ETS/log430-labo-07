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
INSTANCE_ID = os.getenv("INSTANCE_ID", "ecommerce-api-1")

# Métriques principales avec instance_id
REQUEST_COUNT = Counter(
    "ecommerce_api_requests_total",
    "Total API requests",
    ["method", "endpoint", "status_code", "instance_id"],
)

REQUEST_DURATION = Histogram(
    "ecommerce_api_request_duration_seconds",
    "API request duration in seconds",
    ["method", "endpoint", "instance_id"],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

ACTIVE_REQUESTS = Gauge(
    "ecommerce_api_active_requests", "Number of active requests", ["instance_id"]
)

# Métriques temps réel (non cumulatives)
CURRENT_RPS = Gauge(
    "ecommerce_api_current_rps", "Current requests per second", ["instance_id"]
)

ERROR_COUNT = Counter(
    "ecommerce_api_errors_total", "Total API errors", ["error_type", "endpoint", "instance_id"]
)

HEALTH_STATUS = Gauge(
    "ecommerce_api_health_status", "API health status (1=healthy, 0=unhealthy)", ["instance_id"]
)

CPU_USAGE = Gauge(
    "ecommerce_api_cpu_usage_percent", "CPU usage percentage", ["instance_id"]
)

MEMORY_USAGE = Gauge(
    "ecommerce_api_memory_usage_bytes", "Memory usage in bytes", ["instance_id"]
)

MEMORY_USAGE_PERCENT = Gauge(
    "ecommerce_api_memory_usage_percent", "Memory usage percentage", ["instance_id"]
)

# Métriques spécifiques au ecommerce
CUSTOMER_COUNT = Gauge(
    "ecommerce_api_customers_total", "Total number of customers", ["instance_id"]
)

ORDER_COUNT = Counter(
    "ecommerce_api_orders_total", "Total number of orders", ["instance_id", "status"]
)

CART_COUNT = Gauge(
    "ecommerce_api_active_carts_total", "Number of active carts", ["instance_id"]
)

ORDER_REVENUE = Counter(
    "ecommerce_api_order_revenue_total", "Total order revenue", ["instance_id"]
)

CART_OPERATIONS = Counter(
    "ecommerce_api_cart_operations_total", "Total cart operations", ["operation", "instance_id"]
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

    def record_order(self, status: str, amount: float):
        """Enregistre une commande"""
        ORDER_COUNT.labels(instance_id=INSTANCE_ID, status=status).inc()
        ORDER_REVENUE.labels(instance_id=INSTANCE_ID).inc(amount)

    def record_cart_operation(self, operation: str):
        """Enregistre une opération de panier"""
        CART_OPERATIONS.labels(operation=operation, instance_id=INSTANCE_ID).inc()

    def update_customer_count(self, count: int):
        """Met à jour le nombre total de clients"""
        CUSTOMER_COUNT.labels(instance_id=INSTANCE_ID).set(count)

    def update_cart_count(self, count: int):
        """Met à jour le nombre de paniers actifs"""
        CART_COUNT.labels(instance_id=INSTANCE_ID).set(count)

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
            metric.samples[0].value for metric in REQUEST_COUNT.collect()
            for sample in metric.samples
            if sample.labels.get('instance_id') == INSTANCE_ID
        )

        if hasattr(self, 'last_rps_update') and (now - self.last_rps_update) >= 1.0:
            rps = (total_requests - self.last_request_count) / (now - self.last_rps_update)
            CURRENT_RPS.labels(instance_id=INSTANCE_ID).set(max(0, rps))
            self.last_request_count = total_requests
            self.last_rps_update = now

    def get_metrics(self) -> str:
        """Retourne les métriques au format Prometheus"""
        return generate_latest()


# Instance globale du service de métriques
metrics_service = MetricsService() 