import http from 'k6/http';
import { check, sleep } from 'k6';
import { Counter, Rate } from 'k6/metrics';

// Métriques personnalisées
export let errorCount = new Counter('errors');
export let errorRate = new Rate('error_rate');

// Configuration du test pour load balancer
export let options = {
  stages: [
    // Phase 1: Ramp-up progressif
    { duration: '30s', target: 100 },   // 0 → 100 utilisateurs
    { duration: '30s', target: 100 },   // Maintenir 100 utilisateurs
    
    // Phase 2: Escalade modérée
    { duration: '1m', target: 300 },    // 100 → 300 utilisateurs
    { duration: '1m', target: 300 },    // Maintenir 300 utilisateurs
    
    // Phase 3: Stress intensif (devrait mieux résister avec 2 instances)
    { duration: '1m', target: 700 },    // 300 → 700 utilisateurs
    { duration: '1m', target: 700 },    // Maintenir 700 utilisateurs
    
    // Phase 4: Test de limite supérieure
    { duration: '30s', target: 1000 },  // 700 → 1000 utilisateurs
    { duration: '30s', target: 1000 },  // Maintenir 1000 utilisateurs
    
    // Phase 5: Ramp-down
    { duration: '30s', target: 0 },     // Retour à 0
  ],
  thresholds: {
    // Seuils plus tolérants pour load balancer
    http_req_duration: ['p(95)<2000'],  // 95% des requêtes < 2s
    http_req_failed: ['rate<0.1'],      // Moins de 10% d'échecs
    error_rate: ['rate<0.1'],
  },
};

const BASE_URL = 'http://localhost:8000';

// Endpoints à tester
const endpoints = [
  '/api/v1/stores/',
  '/api/v1/products/',
  '/api/v1/products/1',
  '/api/v1/products/2', 
  '/api/v1/reports/global-summary',
  '/health',
  '/metrics',
];

export default function () {
  // Sélectionner un endpoint aléatoire
  const endpoint = endpoints[Math.floor(Math.random() * endpoints.length)];
  const url = `${BASE_URL}${endpoint}`;
  
  // Headers avec API token si nécessaire
  const headers = {
    'X-API-Token': '9645524dac794691257cb44d61ebc8c3d5876363031ec6f66fbd31e4bf85cd84',
    'Content-Type': 'application/json',
  };
  
  // Effectuer la requête
  let response = http.get(url, { headers });
  
  // Vérifier la réponse
  let success = check(response, {
    'status is 200 or 404': (r) => r.status === 200 || r.status === 404,
    'response time < 3000ms': (r) => r.timings.duration < 3000,
  });
  
  if (!success) {
    errorCount.add(1);
    errorRate.add(1);
    console.log(`Error: ${response.status} - ${url} - Duration: ${response.timings.duration}ms`);
  } else {
    errorRate.add(0);
  }
  
  // Pause courte entre les requêtes (simule comportement utilisateur)
  sleep(Math.random() * 0.5 + 0.1); // 0.1 à 0.6 secondes
}

export function handleSummary(data) {
  return {
    'loadbalanced-stress-results.json': JSON.stringify(data, null, 2),
  };
} 