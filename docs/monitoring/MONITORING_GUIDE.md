# 📊 Guide de Monitoring API - LOG430

## 🚀 Démarrage rapide

### 1. Lancer l'API
```bash
docker-compose up -d
```

### 2. Lancer le monitoring
```bash
docker-compose -f docker-compose.monitoring.yml up -d
```

### 3. Accéder aux interfaces

| Service | URL | Identifiants |
|---------|-----|-------------|
| **API** | http://localhost:8000 | - |
| **Prometheus** | http://localhost:9090 | - |
| **Grafana** | http://localhost:3000 | admin / admin |

## 📈 Métriques surveillées

### 1. **Health** (Santé de l'API)
- `up{job="api"}` → 1=API accessible, 0=API down
- `api_health_status` → 1=sain, 0=malade (interne)

### 2. **Traffic** (Trafic)
- `rate(api_requests_total[1m])` → Requêtes par seconde
- Par endpoint et méthode HTTP

### 3. **Latency** (Latence)
- `histogram_quantile(0.95, rate(api_request_duration_seconds_bucket[5m]))` → P95
- `histogram_quantile(0.50, rate(api_request_duration_seconds_bucket[5m]))` → P50 (médiane)

### 4. **Errors** (Erreurs)
- `rate(api_errors_total[1m])` → Erreurs par seconde
- `rate(api_requests_total{status_code=~"4..|5.."}[1m])` → Erreurs HTTP

### 5. **Saturation** (Charge)
- `api_active_requests` → Requêtes en cours
- Indicateur de surcharge

## 🎯 Dashboard Grafana

Le dashboard **"API Performance Dashboard"** contient :

- 🟢 **API Status** → Statut externe (Prometheus peut-il scraper ?)
- ❤️ **API Health** → Santé interne (si API accessible)
- 📈 **Traffic** → Taux de requêtes en temps réel
- ⏱️ **Latency** → Temps de réponse (P50, P95, P99)
- ❌ **Errors** → Taux d'erreur par type
- 🚦 **Saturation** → Charge active et load

## 🧪 Tests de stress avec métriques

### Lancer un test K6
```bash
k6 run k6-tests/simple-stress-test.js
```

### Pendant le test, observez :
1. **Traffic** augmente progressivement
2. **Latency** monte avec la charge
3. **Errors** apparaissent si API surchargée
4. **Saturation** montre la charge active

### Si l'API crash :
- **API Status** → 🔴 API DOWN
- **API Health** → Pas de données
- **Alerte** déclenchée après 30s

## 🚨 Alertes configurées

- **APIDown** → API inaccessible > 30s (CRITIQUE)
- **APIHighErrorRate** → > 10 erreurs/sec (WARNING)
- **APIHighLatency** → P95 > 2s (WARNING)
- **APIHighLoad** → > 100 requêtes actives (WARNING)

## 🔧 Comparaison avant/après améliorations

Pour comparer les performances :

1. **Avant** → Lancez test + capturez métriques Grafana
2. **Améliorations** → Modifiez le code
3. **Après** → Relancez test + comparez métriques

### Métriques clés à comparer :
- **P95 Latency** → Plus bas = mieux
- **Request Rate** → Plus haut = mieux
- **Error Rate** → Plus bas = mieux  
- **Point de rupture** → Charge max avant crash

## 📚 Endpoints utiles

- **Métriques Prometheus** : `http://localhost:8000/metrics`
- **Health API** : `http://localhost:8000/health`
- **API Token** : `9645524dac794691257cb44d61ebc8c3d5876363031ec6f66fbd31e4bf85cd84`

## 🛠️ Commandes utiles

```bash
# Voir les logs de l'API
docker-compose logs -f api

# Redémarrer le monitoring
docker-compose -f docker-compose.monitoring.yml restart

# Arrêter tout
docker-compose down
docker-compose -f docker-compose.monitoring.yml down
``` 