import http from 'k6/http';
import { check, sleep } from 'k6';
import { Counter, Rate } from 'k6/metrics';

// Métriques personnalisées
export const cacheHits = new Counter('cache_hits');
export const cacheMisses = new Counter('cache_misses');
export const loadBalancerDistribution = new Counter('load_balancer_requests');
export const errorRate = new Rate('errors');

export let options = {
  stages: [
    { duration: '1m', target: 30 },    // Démarrage doux
    { duration: '2m', target: 100 },   // Montée progressive
    { duration: '3m', target: 200 },   // Charge moyenne
    { duration: '2m', target: 300 },   // Pic à 300 utilisateurs
    { duration: '4m', target: 300 },   // Maintien du pic
    { duration: '2m', target: 150 },   // Descente progressive
    { duration: '1m', target: 0 },     // Arrêt
  ],
  thresholds: {
    http_req_duration: ['p(95)<1000'],     // 95% des requêtes sous 1 seconde
    http_req_failed: ['rate<0.1'],         // Moins de 10% d'erreurs
    http_reqs: ['rate>30'],                // Au moins 30 req/s
    cache_hits: ['count>50'],              // Au moins 50 cache hits
    errors: ['rate<0.15'],                 // Moins de 15% d'erreurs
  }
};

const BASE_URL = 'http://localhost:8000';
const API_TOKEN = '9645524dac794691257cb44d61ebc8c3d5876363031ec6f66fbd31e4bf85cd84';

const headers = {
  'X-API-Token': API_TOKEN,
  'Content-Type': 'application/json'
};

// Pool d'endpoints à tester avec pondération
const endpoints = [
  { path: '/api/v1/products/', weight: 40, cacheable: true },
  { path: '/api/v1/stores/', weight: 20, cacheable: true },
  { path: '/api/v1/products/1', weight: 15, cacheable: true },
  { path: '/api/v1/products/2', weight: 10, cacheable: true },
  { path: '/api/v1/reports/global-summary', weight: 10, cacheable: true },
  { path: '/health', weight: 5, cacheable: false }
];

// Fonction pour sélectionner un endpoint selon la pondération
function selectEndpoint() {
  const random = Math.random() * 100;
  let cumulative = 0;
  
  for (let endpoint of endpoints) {
    cumulative += endpoint.weight;
    if (random <= cumulative) {
      return endpoint;
    }
  }
  return endpoints[0]; // fallback
}

export default function() {
  const endpoint = selectEndpoint();
  const url = `${BASE_URL}${endpoint.path}`;
  
  // Requête principale
  const response = http.get(url, { headers });
  
  // Vérifications de base
  const success = check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 1000ms': (r) => r.timings.duration < 1000,
    'has content': (r) => r.body && r.body.length > 0,
    'has instance header': (r) => r.headers['X-Instance-Id'] !== undefined,
  });
  
  if (!success) {
    errorRate.add(1);
  }
  
  // Suivi de la distribution du load balancer
  const instanceId = response.headers['X-Instance-Id'];
  if (instanceId) {
    loadBalancerDistribution.add(1, { instance: instanceId });
  }
  
  // Détection du cache (temps de réponse rapide = probablement en cache)
  if (endpoint.cacheable && response.status === 200) {
    if (response.timings.duration < 50) {
      cacheHits.add(1);
    } else if (response.timings.duration > 200) {
      cacheMisses.add(1);
    }
  }
  
  // Pattern de requêtes plus réaliste - parfois plusieurs requêtes par utilisateur
  if (Math.random() < 0.3) {
    sleep(0.1); // Petit délai
    
    // Requête supplémentaire - simule un utilisateur qui navigue
    const secondEndpoint = selectEndpoint();
    const secondResponse = http.get(`${BASE_URL}${secondEndpoint.path}`, { headers });
    
    check(secondResponse, {
      'second request success': (r) => r.status === 200,
    });
    
    if (secondEndpoint.cacheable && secondResponse.status === 200) {
      if (secondResponse.timings.duration < 50) {
        cacheHits.add(1);
      } else if (secondResponse.timings.duration > 200) {
        cacheMisses.add(1);
      }
    }
  }
  
  // Pause réaliste entre les requêtes utilisateur
  sleep(Math.random() * 2 + 0.5); // Entre 0.5 et 2.5 secondes
}

export function handleSummary(data) {
  return {
    'medium-load-test-results.json': JSON.stringify(data, null, 2),
    stdout: `
═══════════════════════════════════════════════════════════════
                    RÉSULTATS TEST 300 UTILISATEURS
═══════════════════════════════════════════════════════════════

📊 MÉTRIQUES PRINCIPALES:
  • Requêtes totales: ${data.metrics.http_reqs.values.count}
  • Requêtes/sec (avg): ${data.metrics.http_reqs.values.rate.toFixed(2)}
  • Durée moyenne: ${data.metrics.http_req_duration.values.avg.toFixed(2)}ms
  • P95 latence: ${data.metrics.http_req_duration.values['p(95)'].toFixed(2)}ms
  • Taux d'erreur: ${(data.metrics.http_req_failed.values.rate * 100).toFixed(2)}%

🏆 PERFORMANCE CACHE:
  • Cache hits: ${data.metrics.cache_hits ? data.metrics.cache_hits.values.count : 0}
  • Cache misses: ${data.metrics.cache_misses ? data.metrics.cache_misses.values.count : 0}
  • Ratio estimé: ${data.metrics.cache_hits && data.metrics.cache_misses ? 
    ((data.metrics.cache_hits.values.count / (data.metrics.cache_hits.values.count + data.metrics.cache_misses.values.count)) * 100).toFixed(1) + '%' : 'N/A'}

🎯 SEUILS:
  • Latence P95 < 1000ms: ${data.metrics.http_req_duration.values['p(95)'] < 1000 ? '✅ PASSÉ' : '❌ ÉCHOUÉ'}
  • Erreurs < 10%: ${data.metrics.http_req_failed.values.rate < 0.1 ? '✅ PASSÉ' : '❌ ÉCHOUÉ'}
  • Throughput > 30 req/s: ${data.metrics.http_reqs.values.rate > 30 ? '✅ PASSÉ' : '❌ ÉCHOUÉ'}

═══════════════════════════════════════════════════════════════
    `
  };
} 