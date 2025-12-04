// PM2 Ecosystem Configuration with Automatic Migrations
// This version runs migrations automatically before starting the backend

module.exports = {
  apps: [{
    name: 'pms-backend',
    // Use the wrapper script instead of calling uvicorn directly
    script: 'powershell.exe',  // On Linux, use: 'bash'
    args: '-ExecutionPolicy Bypass -File start-with-migrations.ps1',  // On Linux, use: 'start-with-migrations.sh'
    cwd: 'C:/Users/vem/pms-stable/backend',
    env: {
      ENVIRONMENT: 'production',
      DATABASE_URL: 'postgresql://pms_user:pms_password@172.28.0.1:5432/pms_db',
      JWT_SECRET_KEY: 'your-super-secret-jwt-key-change-in-production',
      CORS_ALLOWED_ORIGINS: 'http://localhost:3000,https://localhost:3000,http://localhost:3002,https://localhost:3002,http://160.226.0.67:3000,http://160.226.0.67:3002'
    },
    autorestart: true,
    watch: false,
    max_memory_restart: '500M',
    // Restart delay to avoid rapid restarts if migrations fail
    restart_delay: 5000,
    // Kill timeout
    kill_timeout: 5000
  }]
};
