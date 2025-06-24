import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Métriques personnalisées
export let errorRate = new Rate('errors');

// Configuration du test de stress - 5 minutes intensif
export let options = {
  stages: [
    { duration: '20s', target: 50 },   // Démarrage rapide à 50 utilisateurs
    { duration: '30s', target: 100 },  // Montée à 100 utilisateurs
    { duration: '40s', target: 200 },  // Montée à 200 utilisateurs
    { duration: '50s', target: 350 },  // Montée à 350 utilisateurs
    { duration: '60s', target: 500 },  // Peak à 500 utilisateurs
    { duration: '40s', target: 700 },  // STRESS MAXIMUM à 700 utilisateurs
    { duration: '40s', target: 0 },    // Redescente brutale
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'], // 95% des requêtes < 2s (plus tolérant)
    http_req_failed: ['rate<0.15'],    // Moins de 15% d'erreurs (on s'attend à du stress)
    errors: ['rate<0.15'],             // Moins de 15% d'erreurs métier
  },
};

// Configuration de l'API
const BASE_URL = 'http://localhost:8000';
const API_TOKEN = '9645524dac794691257cb44d61ebc8c3d5876363031ec6f66fbd31e4bf85cd84';

const headers = {
  'X-API-Token': API_TOKEN,
  'Content-Type': 'application/json',
};

// Liste des endpoints à tester avec leurs poids
const endpoints = [
  { method: 'GET', url: '/health', weight: 10, needAuth: false },
  { method: 'GET', url: '/api/v1/products/', weight: 30, needAuth: true },
  { method: 'GET', url: '/api/v1/products/1', weight: 20, needAuth: true },
  { method: 'GET', url: '/api/v1/products/2', weight: 15, needAuth: true },
  { method: 'GET', url: '/api/v1/stores/', weight: 15, needAuth: true },
  { method: 'GET', url: '/api/v1/reports/global-summary', weight: 10, needAuth: true },
];

// Fonction pour choisir un endpoint selon les poids
function selectEndpoint() {
  const totalWeight = endpoints.reduce((sum, ep) => sum + ep.weight, 0);
  let random = Math.random() * totalWeight;
  
  for (let endpoint of endpoints) {
    random -= endpoint.weight;
    if (random <= 0) {
      return endpoint;
    }
  }
  return endpoints[0]; // fallback
}

export default function () {
  // Sélectionner un endpoint aléatoirement selon les poids
  const endpoint = selectEndpoint();
  
  // Préparer les headers
  const requestHeaders = endpoint.needAuth ? headers : {};
  
  // Faire la requête
  const response = http.request(
    endpoint.method,
    `${BASE_URL}${endpoint.url}`,
    null,
    { headers: requestHeaders }
  );
  
  // Vérifications
  const success = check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 2s': (r) => r.timings.duration < 2000,
    'response has body': (r) => r.body && r.body.length > 0,
  });
  
  // Compter les erreurs (seulement les vraies erreurs)
  const isRealError = response.status === 0 || response.status >= 400;
  errorRate.add(isRealError);
  
  // Log des erreurs pour debug (seulement les vraies erreurs)
  if (isRealError) {
    console.log(`🚨 REAL ERROR on ${endpoint.method} ${endpoint.url}: Status ${response.status}`);
    console.log(`Response body: ${response.body}`);
  } else if (response.timings.duration > 1000) {
    console.log(`⚠️ SLOW response on ${endpoint.method} ${endpoint.url}: ${Math.round(response.timings.duration)}ms`);
  }
  
  // Pause très courte pour augmenter le stress
  sleep(Math.random() * 0.2 + 0.05); // 0.05 à 0.25 secondes (plus agressif)
}

export function handleSummary(data) {
  return {
    'stdout': textSummary(data, { indent: ' ', enableColors: true }),
    'results/stress-5min-results.json': JSON.stringify(data, null, 2),
  };
}

function textSummary(data, options = {}) {
  const indent = options.indent || '';
  const colors = options.enableColors;
  
  let summary = `
${indent}🔥 Test de Stress INTENSIF (5min) - Résultats
${indent}═══════════════════════════════════════════

${indent}📈 Métriques de Performance:
${indent}• Requêtes totales: ${data.metrics.http_reqs.values.count}
${indent}• Durée moyenne: ${Math.round(data.metrics.http_req_duration.values.avg)}ms
${indent}• P95: ${Math.round(data.metrics.http_req_duration.values['p(95)'])}ms
${indent}• P99: ${Math.round(data.metrics.http_req_duration.values['p(99)'])}ms

${indent}✅ Taux de Succès:
${indent}• Requêtes réussies: ${Math.round((1 - data.metrics.http_req_failed.values.rate) * 100)}%
${indent}• Erreurs HTTP: ${Math.round(data.metrics.http_req_failed.values.rate * 100)}%

${indent}🔥 Charge:
${indent}• Req/sec max: ${Math.round(data.metrics.http_reqs.values.rate)}
${indent}• Utilisateurs max: ${data.metrics.vus_max.values.max}

${indent}🎯 Seuils:
${indent}• P95 < 1000ms: ${data.metrics.http_req_duration.thresholds['p(95)<1000'].ok ? '✅' : '❌'}
${indent}• Erreurs < 5%: ${data.metrics.http_req_failed.thresholds['rate<0.05'].ok ? '✅' : '❌'}
`;

  return summary;
} 