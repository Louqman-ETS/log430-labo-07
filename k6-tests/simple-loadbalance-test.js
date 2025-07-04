import http from 'k6/http';
import { check } from 'k6';

export const options = {
  vus: 10,        // 10 utilisateurs virtuels
  duration: '30s', // Test de 30 secondes
};

const BASE_URL = 'http://localhost:9000';
const API_KEY = 'admin-api-key-12345';

// Compteurs pour la distribution
let instanceCounts = {};

export default function () {
  const headers = { 'apikey': API_KEY };

  // Test du endpoint racine pour voir l'instance
  const response = http.get(`${BASE_URL}/inventory/`, { headers });
  
  check(response, {
    'Status is 200': (r) => r.status === 200,
    'Has instance ID': (r) => r.json('instance') !== undefined,
  });

  // Compter les instances
  if (response.status === 200) {
    const instance = response.json('instance');
    if (instance) {
      instanceCounts[instance] = (instanceCounts[instance] || 0) + 1;
    }
  }
}

export function handleSummary(data) {
  console.log('\n=== RÉSULTATS DU LOAD BALANCING ===');
  
  const total = Object.values(instanceCounts).reduce((a, b) => a + b, 0);
  
  for (const [instance, count] of Object.entries(instanceCounts)) {
    const percentage = ((count / total) * 100).toFixed(1);
    console.log(`${instance}: ${count} requêtes (${percentage}%)`);
  }
  
  console.log(`\nTotal: ${total} requêtes distribuées`);
  
  // Vérification de l'équilibrage
  const instances = Object.keys(instanceCounts).length;
  const expectedPerInstance = total / instances;
  const maxDeviation = Math.max(...Object.values(instanceCounts)) - Math.min(...Object.values(instanceCounts));
  
  const isBalanced = maxDeviation <= (expectedPerInstance * 0.2); // Tolérance de 20%
  
  console.log(`\nÉquilibrage: ${isBalanced ? '✅ BON' : '❌ DÉSÉQUILIBRÉ'}`);
  console.log(`Écart max: ${maxDeviation} requêtes`);
  
  return {
    'stdout': JSON.stringify(data, null, 2),
  };
} 