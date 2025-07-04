import http from 'k6/http';
import { check, sleep } from 'k6';
import { Counter, Rate } from 'k6/metrics';

// Métriques personnalisées pour le load balancing
const instanceCounter = new Counter('instance_requests');
const errorRate = new Rate('error_rate');

// Configuration du test de charge
export const options = {
  stages: [
    { duration: '30s', target: 10 },  // Montée progressive
    { duration: '1m', target: 50 },   // Charge modérée
    { duration: '2m', target: 100 },  // Charge élevée
    { duration: '30s', target: 0 },   // Descente
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% des requêtes < 500ms
    error_rate: ['rate<0.1'],         // Moins de 10% d'erreurs
    checks: ['rate>0.9'],             // Plus de 90% de succès
  },
};

const BASE_URL = 'http://localhost:9000';
const API_KEY = 'admin-api-key-12345';

// Compteurs pour suivre la distribution des instances
let instanceStats = {
  'inventory-api-1': 0,
  'inventory-api-2': 0,
  'inventory-api-3': 0,
  'unknown': 0
};

export default function () {
  const headers = {
    'apikey': API_KEY,
    'Content-Type': 'application/json',
  };

  // Test 1: Endpoint racine (pour voir l'instance)
  let response = http.get(`${BASE_URL}/inventory/`, { headers });
  
  const success = check(response, {
    'Status is 200': (r) => r.status === 200,
    'Response time < 500ms': (r) => r.timings.duration < 500,
    'Has instance ID': (r) => r.json('instance') !== undefined,
  });

  if (!success) {
    errorRate.add(1);
  } else {
    errorRate.add(0);
    
    // Compter les instances qui répondent
    const instanceId = response.json('instance');
    if (instanceId && instanceStats.hasOwnProperty(instanceId)) {
      instanceStats[instanceId]++;
      instanceCounter.add(1, { instance: instanceId });
    } else {
      instanceStats['unknown']++;
      instanceCounter.add(1, { instance: 'unknown' });
    }
  }

  // Test 2: Liste des produits
  response = http.get(`${BASE_URL}/inventory/api/v1/products/`, { headers });
  check(response, {
    'Products endpoint works': (r) => r.status === 200,
    'Products response time < 1s': (r) => r.timings.duration < 1000,
  });

  // Test 3: Health check
  response = http.get(`${BASE_URL}/inventory/health`, { headers });
  check(response, {
    'Health check works': (r) => r.status === 200,
    'Health has instance ID': (r) => r.json('instance') !== undefined,
  });

  // Test 4: Requête concurrente (stock check)
  response = http.get(`${BASE_URL}/inventory/api/v1/stock/`, { headers });
  check(response, {
    'Stock endpoint works': (r) => r.status === 200,
  });

  sleep(1); // Pause entre les requêtes
}

export function handleSummary(data) {
  // Afficher les statistiques de distribution des instances
  const totalRequests = Object.values(instanceStats).reduce((a, b) => a + b, 0);
  
  console.log('\n=== DISTRIBUTION DES INSTANCES ===');
  for (const [instance, count] of Object.entries(instanceStats)) {
    const percentage = totalRequests > 0 ? ((count / totalRequests) * 100).toFixed(2) : 0;
    console.log(`${instance}: ${count} requêtes (${percentage}%)`);
  }
  
  console.log(`\nTotal: ${totalRequests} requêtes`);
  
  // Vérifier si la distribution est équilibrée (tolérance de ±5%)
  const expectedPercentage = 100 / 3; // 33.33% pour 3 instances
  const tolerance = 5;
  
  let balanced = true;
  for (const [instance, count] of Object.entries(instanceStats)) {
    if (instance === 'unknown') continue;
    const percentage = totalRequests > 0 ? (count / totalRequests) * 100 : 0;
    if (Math.abs(percentage - expectedPercentage) > tolerance) {
      balanced = false;
    }
  }
  
  console.log(`\nLoad balancing ${balanced ? '✅ ÉQUILIBRÉ' : '❌ DÉSÉQUILIBRÉ'}`);
  console.log(`Tolérance: ±${tolerance}% (attendu: ~${expectedPercentage.toFixed(1)}% par instance)`);

  return {
    'stdout': JSON.stringify(data, null, 2),
    'loadbalancing-summary.json': JSON.stringify({
      summary: data,
      loadBalancing: {
        instanceStats,
        totalRequests,
        balanced,
        expectedPercentage,
        tolerance
      }
    }, null, 2),
  };
} 