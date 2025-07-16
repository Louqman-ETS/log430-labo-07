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
INSTANCE_ID = os.getenv("INSTANCE_ID", "saga-orchestrator-1")

# Métriques principales avec instance_id
REQUEST_COUNT = Counter(
    "saga_orchestrator_requests_total",
    "Total API requests",
    ["method", "endpoint", "status_code", "instance_id"],
)

REQUEST_DURATION = Histogram(
    "saga_orchestrator_request_duration_seconds",
    "API request duration in seconds",
    ["method", "endpoint", "instance_id"],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

ACTIVE_REQUESTS = Gauge(
    "saga_orchestrator_active_requests", "Number of active requests", ["instance_id"]
)

# Métriques spécifiques aux sagas
SAGA_COUNT = Counter(
    "saga_orchestrator_sagas_total",
    "Total number of sagas",
    ["saga_type", "status", "instance_id"],
)

SAGA_DURATION = Histogram(
    "saga_orchestrator_saga_duration_seconds",
    "Saga execution duration in seconds",
    ["saga_type", "status", "instance_id"],
    buckets=[0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 300.0],
)

SAGA_STEP_COUNT = Counter(
    "saga_orchestrator_saga_steps_total",
    "Total number of saga steps",
    ["saga_type", "step", "status", "instance_id"],
)

SAGA_STEP_DURATION = Histogram(
    "saga_orchestrator_saga_step_duration_seconds",
    "Saga step execution duration in seconds",
    ["saga_type", "step", "instance_id"],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

SAGA_COMPENSATION_COUNT = Counter(
    "saga_orchestrator_compensations_total",
    "Total number of compensations",
    ["saga_type", "compensation_step", "instance_id"],
)

ACTIVE_SAGAS = Gauge(
    "saga_orchestrator_active_sagas",
    "Number of currently active sagas",
    ["saga_type", "state", "instance_id"],
)

SAGA_SUCCESS_RATE = Gauge(
    "saga_orchestrator_saga_success_rate",
    "Success rate of sagas (0-1)",
    ["saga_type", "instance_id"],
)

# Métriques d'erreur
ERROR_COUNT = Counter(
    "saga_orchestrator_errors_total",
    "Total API errors",
    ["error_type", "endpoint", "instance_id"],
)

# Métriques système
HEALTH_STATUS = Gauge(
    "saga_orchestrator_health_status",
    "API health status (1=healthy, 0=unhealthy)",
    ["instance_id"],
)

CPU_USAGE = Gauge(
    "saga_orchestrator_cpu_usage_percent", "CPU usage percentage", ["instance_id"]
)

MEMORY_USAGE = Gauge(
    "saga_orchestrator_memory_usage_bytes", "Memory usage in bytes", ["instance_id"]
)

MEMORY_USAGE_PERCENT = Gauge(
    "saga_orchestrator_memory_usage_percent", "Memory usage percentage", ["instance_id"]
)


class MetricsService:
    """Service pour la gestion des métriques Prometheus"""

    def __init__(self):
        self.start_time = time.time()
        self.request_times = {}
        self._update_system_metrics()
        
        # Démarrer le thread de mise à jour des métriques système
        self._start_system_metrics_thread()

    def record_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Enregistre une requête HTTP"""
        REQUEST_COUNT.labels(
            method=method, 
            endpoint=endpoint, 
            status_code=status_code, 
            instance_id=INSTANCE_ID
        ).inc()
        
        REQUEST_DURATION.labels(
            method=method, 
            endpoint=endpoint, 
            instance_id=INSTANCE_ID
        ).observe(duration)

    def start_request(self, request_id: str):
        """Marque le début d'une requête"""
        ACTIVE_REQUESTS.labels(instance_id=INSTANCE_ID).inc()
        self.request_times[request_id] = time.time()

    def end_request(self, request_id: str):
        """Marque la fin d'une requête"""
        ACTIVE_REQUESTS.labels(instance_id=INSTANCE_ID).dec()
        if request_id in self.request_times:
            del self.request_times[request_id]

    def record_saga_started(self, saga_type: str):
        """Enregistre le début d'une saga"""
        SAGA_COUNT.labels(
            saga_type=saga_type, 
            status="started", 
            instance_id=INSTANCE_ID
        ).inc()

    def record_saga_completed(self, saga_type: str, duration: float):
        """Enregistre la completion d'une saga"""
        SAGA_COUNT.labels(
            saga_type=saga_type, 
            status="completed", 
            instance_id=INSTANCE_ID
        ).inc()
        
        SAGA_DURATION.labels(
            saga_type=saga_type, 
            status="completed", 
            instance_id=INSTANCE_ID
        ).observe(duration)

    def record_saga_failed(self, saga_type: str, duration: float):
        """Enregistre l'échec d'une saga"""
        SAGA_COUNT.labels(
            saga_type=saga_type, 
            status="failed", 
            instance_id=INSTANCE_ID
        ).inc()
        
        SAGA_DURATION.labels(
            saga_type=saga_type, 
            status="failed", 
            instance_id=INSTANCE_ID
        ).observe(duration)

    def record_saga_step(self, saga_type: str, step: str, status: str, duration: Optional[float] = None):
        """Enregistre l'exécution d'une étape de saga"""
        SAGA_STEP_COUNT.labels(
            saga_type=saga_type, 
            step=step, 
            status=status, 
            instance_id=INSTANCE_ID
        ).inc()
        
        if duration is not None:
            SAGA_STEP_DURATION.labels(
                saga_type=saga_type, 
                step=step, 
                instance_id=INSTANCE_ID
            ).observe(duration)

    def record_compensation(self, saga_type: str, compensation_step: str):
        """Enregistre une compensation"""
        SAGA_COMPENSATION_COUNT.labels(
            saga_type=saga_type, 
            compensation_step=compensation_step, 
            instance_id=INSTANCE_ID
        ).inc()

    def update_active_sagas(self, saga_type: str, state: str, count: int):
        """Met à jour le nombre de sagas actives"""
        ACTIVE_SAGAS.labels(
            saga_type=saga_type, 
            state=state, 
            instance_id=INSTANCE_ID
        ).set(count)

    def update_success_rate(self, saga_type: str, success_rate: float):
        """Met à jour le taux de succès des sagas"""
        SAGA_SUCCESS_RATE.labels(
            saga_type=saga_type, 
            instance_id=INSTANCE_ID
        ).set(success_rate)

    def record_error(self, error_type: str, endpoint: str):
        """Enregistre une erreur"""
        ERROR_COUNT.labels(
            error_type=error_type, 
            endpoint=endpoint, 
            instance_id=INSTANCE_ID
        ).inc()

    def set_health_status(self, healthy: bool):
        """Met à jour le statut de santé"""
        HEALTH_STATUS.labels(instance_id=INSTANCE_ID).set(1 if healthy else 0)

    def _update_system_metrics(self):
        """Met à jour les métriques système"""
        try:
            # Métriques CPU
            cpu_percent = psutil.cpu_percent(interval=None)
            CPU_USAGE.labels(instance_id=INSTANCE_ID).set(cpu_percent)
            
            # Métriques mémoire
            memory = psutil.virtual_memory()
            MEMORY_USAGE.labels(instance_id=INSTANCE_ID).set(memory.used)
            MEMORY_USAGE_PERCENT.labels(instance_id=INSTANCE_ID).set(memory.percent)
            
        except Exception as e:
            # En cas d'erreur, ne pas faire échouer l'application
            pass

    def _start_system_metrics_thread(self):
        """Démarre le thread de mise à jour des métriques système"""
        def update_loop():
            while True:
                try:
                    self._update_system_metrics()
                    time.sleep(15)  # Mise à jour toutes les 15 secondes
                except Exception:
                    time.sleep(15)
        
        thread = threading.Thread(target=update_loop, daemon=True)
        thread.start()

    def get_metrics(self) -> str:
        """Retourne les métriques au format Prometheus"""
        return generate_latest()


# Instance globale du service de métriques
metrics_service = MetricsService()

# Exporter les constantes pour les autres modules
__all__ = ["metrics_service", "CONTENT_TYPE_LATEST"] 