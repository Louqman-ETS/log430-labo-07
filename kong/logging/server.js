const express = require('express');
const fs = require('fs');
const path = require('path');
const morgan = require('morgan');

const app = express();
const PORT = 3000;

// Middleware
app.use(express.json({ limit: '10mb' }));
app.use(morgan('combined'));

// Créer le répertoire de logs s'il n'existe pas
const logsDir = path.join(__dirname, 'logs');
if (!fs.existsSync(logsDir)) {
    fs.mkdirSync(logsDir, { recursive: true });
}

// Fonction pour formater la date
function getTimestamp() {
    return new Date().toISOString();
}

// Fonction pour écrire les logs dans un fichier
function writeLogToFile(logData, logType = 'access') {
    const timestamp = getTimestamp();
    const logEntry = {
        timestamp,
        type: logType,
        ...logData
    };
    
    const logFileName = path.join(logsDir, `kong-${logType}-${new Date().toISOString().split('T')[0]}.log`);
    const logLine = JSON.stringify(logEntry) + '\n';
    
    fs.appendFileSync(logFileName, logLine);
}

// Route principale pour recevoir les logs de Kong
app.post('/logs', (req, res) => {
    try {
        const logData = req.body;
        
        // Déterminer le type de log
        let logType = 'access';
        if (logData.response && logData.response.status >= 400) {
            logType = 'error';
        } else if (logData.request && logData.request.method) {
            logType = 'access';
        }
        
        // Enrichir les données de log
        const enrichedLog = {
            service: logData.service?.name || 'unknown',
            route: logData.route?.name || 'unknown',
            consumer: logData.consumer?.username || 'anonymous',
            request: {
                method: logData.request?.method,
                url: logData.request?.url,
                size: logData.request?.size,
                headers: logData.request?.headers
            },
            response: {
                status: logData.response?.status,
                size: logData.response?.size,
                headers: logData.response?.headers
            },
            latencies: logData.latencies,
            client_ip: logData.client_ip,
            started_at: logData.started_at
        };
        
        // Écrire dans le fichier
        writeLogToFile(enrichedLog, logType);
        
        // Log sur la console pour debug
        console.log(`📊 [${getTimestamp()}] ${logType.toUpperCase()}: ${enrichedLog.request.method} ${enrichedLog.request.url} - ${enrichedLog.response.status} (${enrichedLog.service}/${enrichedLog.route})`);
        
        res.status(200).json({ 
            message: 'Log received and stored',
            timestamp: getTimestamp()
        });
        
    } catch (error) {
        console.error('❌ Erreur lors du traitement des logs:', error);
        res.status(500).json({ 
            error: 'Internal server error',
            message: error.message 
        });
    }
});

// Route pour consulter les logs récents
app.get('/logs/recent', (req, res) => {
    try {
        const today = new Date().toISOString().split('T')[0];
        const accessLogFile = path.join(logsDir, `kong-access-${today}.log`);
        const errorLogFile = path.join(logsDir, `kong-error-${today}.log`);
        
        let logs = [];
        
        // Lire les logs d'accès
        if (fs.existsSync(accessLogFile)) {
            const accessLogs = fs.readFileSync(accessLogFile, 'utf8')
                .split('\n')
                .filter(line => line.trim())
                .map(line => JSON.parse(line));
            logs = logs.concat(accessLogs);
        }
        
        // Lire les logs d'erreur
        if (fs.existsSync(errorLogFile)) {
            const errorLogs = fs.readFileSync(errorLogFile, 'utf8')
                .split('\n')
                .filter(line => line.trim())
                .map(line => JSON.parse(line));
            logs = logs.concat(errorLogs);
        }
        
        // Trier par timestamp (plus récent en premier)
        logs.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
        
        // Limiter à 100 entrées
        const limit = parseInt(req.query.limit) || 100;
        logs = logs.slice(0, limit);
        
        res.json({
            total: logs.length,
            logs: logs
        });
        
    } catch (error) {
        console.error('❌ Erreur lors de la lecture des logs:', error);
        res.status(500).json({ 
            error: 'Internal server error',
            message: error.message 
        });
    }
});

// Route pour les statistiques
app.get('/logs/stats', (req, res) => {
    try {
        const today = new Date().toISOString().split('T')[0];
        const accessLogFile = path.join(logsDir, `kong-access-${today}.log`);
        
        if (!fs.existsSync(accessLogFile)) {
            return res.json({
                total_requests: 0,
                by_service: {},
                by_status: {},
                by_method: {}
            });
        }
        
        const logs = fs.readFileSync(accessLogFile, 'utf8')
            .split('\n')
            .filter(line => line.trim())
            .map(line => JSON.parse(line));
        
        const stats = {
            total_requests: logs.length,
            by_service: {},
            by_status: {},
            by_method: {}
        };
        
        logs.forEach(log => {
            // Par service
            const service = log.service || 'unknown';
            stats.by_service[service] = (stats.by_service[service] || 0) + 1;
            
            // Par status
            const status = log.response?.status || 'unknown';
            stats.by_status[status] = (stats.by_status[status] || 0) + 1;
            
            // Par méthode
            const method = log.request?.method || 'unknown';
            stats.by_method[method] = (stats.by_method[method] || 0) + 1;
        });
        
        res.json(stats);
        
    } catch (error) {
        console.error('❌ Erreur lors du calcul des statistiques:', error);
        res.status(500).json({ 
            error: 'Internal server error',
            message: error.message 
        });
    }
});

// Route de santé
app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        service: 'kong-logging-service',
        timestamp: getTimestamp(),
        uptime: process.uptime()
    });
});

// Démarrer le serveur
app.listen(PORT, '0.0.0.0', () => {
    console.log(`🚀 Kong Logging Service démarré sur le port ${PORT}`);
    console.log(`📊 Logs stockés dans: ${logsDir}`);
    console.log(`🏥 Health check: http://localhost:${PORT}/health`);
    console.log(`📋 Logs récents: http://localhost:${PORT}/logs/recent`);
    console.log(`📈 Statistiques: http://localhost:${PORT}/logs/stats`);
});

// Gestion graceful shutdown
process.on('SIGTERM', () => {
    console.log('🛑 Arrêt graceful du service de logging');
    process.exit(0);
});

process.on('SIGINT', () => {
    console.log('🛑 Arrêt graceful du service de logging');
    process.exit(0);
}); 