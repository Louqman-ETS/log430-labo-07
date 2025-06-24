from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from typing import Optional
import time
import psutil
import os
import threading

# Récupérer l'ID d'instance depuis les variables d'environnement
INSTANCE_ID = os.getenv('INSTANCE_ID', 'api-1')

# Métriques principales avec instance_id
REQUEST_COUNT = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status_code', 'instance_id']
)

REQUEST_DURATION = Histogram(
    'api_request_duration_seconds',
    'API request duration in seconds',
    ['method', 'endpoint', 'instance_id']
)

ACTIVE_REQUESTS = Gauge(
    'api_active_requests',
    'Number of active requests',
    ['instance_id']
)

# Métriques temps réel (non cumulatives)
CURRENT_RPS = Gauge(
    'api_current_rps',
    'Current requests per second (calculated)',
    ['instance_id']
)

ERROR_COUNT = Counter(
    'api_errors_total',
    'Total API errors',
    ['error_type', 'endpoint', 'instance_id']
)

HEALTH_STATUS = Gauge(
    'api_health_status',
    'API health status (1=healthy, 0=unhealthy)',
    ['instance_id']
)

CPU_USAGE = Gauge(
    'api_cpu_usage_percent',
    'CPU usage percentage of API process',
    ['instance_id']
)

MEMORY_USAGE = Gauge(
    'api_memory_usage_bytes',
    'Memory usage in bytes of API process',
    ['instance_id']
)

MEMORY_USAGE_PERCENT = Gauge(
    'api_memory_usage_percent',
    'Memory usage percentage of API process',
    ['instance_id']
)

# Métriques pour le cache Redis
CACHE_OPERATIONS = Counter(
    'api_cache_operations_total',
    'Total number of cache operations',
    ['operation', 'instance_id', 'result']
)

CACHE_HIT_RATIO = Gauge(
    'api_cache_hit_ratio',
    'Cache hit ratio (hits / (hits + misses))',
    ['instance_id']
)

CACHE_KEYS_COUNT = Gauge(
    'api_cache_keys_total',
    'Total number of keys in cache',
    ['instance_id']
)

CACHE_MEMORY_USAGE = Gauge(
    'api_cache_memory_bytes',
    'Memory usage of Redis cache in bytes',
    ['instance_id']
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
    
    def record_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Enregistre une requête"""
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code=status_code, instance_id=INSTANCE_ID).inc()
        REQUEST_DURATION.labels(method=method, endpoint=endpoint, instance_id=INSTANCE_ID).observe(duration)
        self._update_current_rps()
    
    def record_error(self, error_type: str, endpoint: str):
        """Enregistre une erreur"""
        ERROR_COUNT.labels(error_type=error_type, endpoint=endpoint, instance_id=INSTANCE_ID).inc()
    
    def set_health_status(self, is_healthy: bool):
        """Met à jour le statut de santé"""
        HEALTH_STATUS.labels(instance_id=INSTANCE_ID).set(1 if is_healthy else 0)
    
    def increment_active_requests(self):
        """Incrémente le nombre de requêtes actives"""
        ACTIVE_REQUESTS.labels(instance_id=INSTANCE_ID).inc()
    
    def decrement_active_requests(self):
        """Décrémente le nombre de requêtes actives"""
        ACTIVE_REQUESTS.labels(instance_id=INSTANCE_ID).dec()
    
    def _start_monitoring_thread(self):
        """Démarre un thread pour monitorer les métriques système en background"""
        def monitor():
            while True:
                try:
                    # CPU usage (utilisation globale du système, plus fiable dans Docker)
                    cpu_percent = psutil.cpu_percent(interval=1)
                    CPU_USAGE.labels(instance_id=INSTANCE_ID).set(cpu_percent)
                    
                    # Memory usage du processus
                    memory_info = self.process.memory_info()
                    MEMORY_USAGE.labels(instance_id=INSTANCE_ID).set(memory_info.rss)  # Resident Set Size en bytes
                    
                    # Memory usage percentage du système global
                    memory_info_system = psutil.virtual_memory()
                    MEMORY_USAGE_PERCENT.labels(instance_id=INSTANCE_ID).set(memory_info_system.percent)
                    
                except Exception as e:
                    # En cas d'erreur, on continue sans crasher
                    print(f"Error updating metrics: {e}")  # Debug
                
                time.sleep(2)  # Mise à jour toutes les 2 secondes
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
    
    def _update_current_rps(self):
        """Met à jour le RPS temps réel basé sur les requêtes récentes"""
        now = time.time()
        current_count = REQUEST_COUNT.labels(method="GET", endpoint="/", status_code=200, instance_id=INSTANCE_ID)._value._value
        
        if hasattr(self, 'last_rps_update') and (now - self.last_rps_update) >= 1.0:  # Mise à jour chaque seconde
            rps = (current_count - self.last_request_count) / (now - self.last_rps_update)
            CURRENT_RPS.labels(instance_id=INSTANCE_ID).set(max(0, rps))
            self.last_request_count = current_count
            self.last_rps_update = now
    
    def update_system_metrics(self):
        """Met à jour les métriques système (CPU, mémoire) - appelé lors du scraping"""
        # Les métriques sont maintenant mises à jour par le thread background
        # Cette méthode peut être gardée pour compatibilité mais ne fait rien
        pass
    
    def get_metrics(self) -> str:
        """Retourne les métriques au format Prometheus"""
        # Mettre à jour les métriques système avant de les retourner
        self.update_system_metrics()
        return generate_latest()

def record_cache_operation(operation: str, result: str):
    """Enregistrer une opération de cache (hit, miss, set, delete)"""
    CACHE_OPERATIONS.labels(
        operation=operation,
        instance_id=INSTANCE_ID,
        result=result
    ).inc()

def update_cache_metrics(stats: dict):
    """Mettre à jour les métriques du cache avec les statistiques Redis"""
    if stats.get('enabled', False) and 'error' not in stats:
        hits = stats.get('hits', 0)
        misses = stats.get('misses', 0)
        total_ops = hits + misses
        
        # Calcul du hit ratio
        if total_ops > 0:
            hit_ratio = hits / total_ops
            CACHE_HIT_RATIO.labels(instance_id=INSTANCE_ID).set(hit_ratio)
        
        # Nombre de clés
        keys_count = stats.get('keys', 0)
        CACHE_KEYS_COUNT.labels(instance_id=INSTANCE_ID).set(keys_count)
        
        # Usage mémoire (convertir depuis le format human-readable si possible)
        memory_str = stats.get('memory_used', '0B')
        try:
            # Tentative de parsing simple pour les unités courantes
            if 'K' in memory_str:
                memory_bytes = float(memory_str.replace('K', '')) * 1024
            elif 'M' in memory_str:
                memory_bytes = float(memory_str.replace('M', '')) * 1024 * 1024
            elif 'G' in memory_str:
                memory_bytes = float(memory_str.replace('G', '')) * 1024 * 1024 * 1024
            else:
                memory_bytes = float(memory_str.replace('B', ''))
            
            CACHE_MEMORY_USAGE.labels(instance_id=INSTANCE_ID).set(memory_bytes)
        except (ValueError, AttributeError):
            pass  # Ignore si on ne peut pas parser

# Instance globale
metrics_service = MetricsService() 