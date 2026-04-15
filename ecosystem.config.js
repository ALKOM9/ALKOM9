module.exports = {
    apps: [{
        name: 'aylin',
        script: 'index.js',
        watch: false,
        instances: 1,
        autorestart: true,
        max_restarts: 10,
        min_uptime: '10s',
        restart_delay: 5000,
        env: {
            NODE_ENV: 'production'
        },
        log_date_format: 'YYYY-MM-DD HH:mm:ss',
        error_file: 'data/logs/pm2-error.log',
        out_file: 'data/logs/pm2-out.log',
        merge_logs: true
    }]
};
