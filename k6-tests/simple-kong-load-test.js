import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
    stages: [
        { duration: '1m', target: 25 },   // Montée à 25 users
        { duration: '1m', target: 50 },   // Montée à 50 users
        { duration: '1m', target: 75 },   // Montée à 75 users
        { duration: '1m', target: 100 },  // Montée à 100 users
        { duration: '4m', target: 100 },  // Maintenir 100 users
        { duration: '2m', target: 0 },    // Descendre à 0
    ],
    thresholds: {
        http_req_failed: ['rate<0.1'],      // Moins de 10% d'erreurs
        http_req_duration: ['p(95)<2000'],  // 95% des requêtes < 2s
        checks: ['rate>0.9'],               // Plus de 90% de succès
    },
};

const BASE_URL = 'http://localhost:9000';
const API_KEY = 'admin-api-key-12345';

// 4 endpoints
const endpoints = [
    {
        name: 'Inventory Products',
        url: `${BASE_URL}/inventory/api/v1/products/?apikey=${API_KEY}`,
        service: 'inventory'
    },
    {
        name: 'Retail Stores', 
        url: `${BASE_URL}/retail/api/v1/stores/?apikey=${API_KEY}`,
        service: 'retail'
    },
    {
        name: 'Ecommerce Customers',
        url: `${BASE_URL}/ecommerce/api/v1/customers/?apikey=${API_KEY}`,
        service: 'ecommerce'
    },
    {
        name: 'Reporting Sales by Period',
        url: `${BASE_URL}/reporting/api/v1/reports/sales-by-period?apikey=${API_KEY}`,
        service: 'reporting'
    }
];

export default function() {
    // Sélectionner un endpoint aléatoire
    const endpoint = endpoints[Math.floor(Math.random() * endpoints.length)];
    
    // Faire la requête
    const response = http.get(endpoint.url, {
        timeout: '10s',
        headers: {
            'Accept': 'application/json',
        }
    });
    
    // Vérifications
    check(response, {
        [`${endpoint.name} - Status 200`]: (r) => r.status === 200,
        [`${endpoint.name} - Response time < 3s`]: (r) => r.timings.duration < 3000,
        [`${endpoint.name} - Has response body`]: (r) => r.body && r.body.length > 0,
    });
    
    // Pause entre les requêtes
    sleep(1);
}

export function handleSummary(data) {
    console.log('\n=== RÉSULTATS DU TEST DE CHARGE SIMPLE - 100 UTILISATEURS / 10 MIN ===');
    console.log(`Durée totale: ${Math.round(data.metrics.iteration_duration.avg)}ms moyenne par itération`);
    console.log(`Total requêtes: ${data.metrics.http_reqs.count}`);
    console.log(`Requêtes/seconde: ${data.metrics.http_reqs.rate.toFixed(2)}`);
    console.log(`Taux d'erreur: ${(data.metrics.http_req_failed.rate * 100).toFixed(2)}%`);
    console.log(`Temps de réponse p95: ${data.metrics.http_req_duration.p95.toFixed(2)}ms`);
    console.log(`Taux de succès des checks: ${(data.metrics.checks.rate * 100).toFixed(2)}%`);
    
    console.log('\n=== DÉTAILS ===');
    console.log(`- Requêtes réussies: ${data.metrics.http_reqs.count - Math.round(data.metrics.http_reqs.count * data.metrics.http_req_failed.rate)}`);
    console.log(`- Requêtes échouées: ${Math.round(data.metrics.http_reqs.count * data.metrics.http_req_failed.rate)}`);
    console.log(`- Temps de réponse moyen: ${data.metrics.http_req_duration.avg.toFixed(2)}ms`);
    console.log(`- Temps de réponse médian: ${data.metrics.http_req_duration.med.toFixed(2)}ms`);
    console.log(`- Temps de réponse max: ${data.metrics.http_req_duration.max.toFixed(2)}ms`);
    
    if (data.metrics.http_req_failed.rate < 0.1) {
        console.log('\n✅ TEST RÉUSSI - Taux d\'erreur acceptable');
    } else {
        console.log('\n❌ TEST ÉCHOUÉ - Trop d\'erreurs');
    }
    
    return {
        'stdout': JSON.stringify(data, null, 2),
    };
} 