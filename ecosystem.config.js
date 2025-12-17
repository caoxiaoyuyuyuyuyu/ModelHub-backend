module.exports = {
  apps: [{
    name: "modelhub-backend",
    // 核心修正：直接使用 Conda 环境的 flask 命令
    script: "/root/miniconda/envs/modelhub/bin/flask",
    args: "run --host=0.0.0.0 --port=5000 --debug",
    interpreter: "none", // 不需要额外指定解释器
    env: {
      FLASK_APP: "app.py",
      FLASK_ENV: "development",
      FLASK_DEBUG: "1",
      // 其他生产环境变量
      // DATABASE_URL: "postgresql://user:prodpass@prod-db.example.com/prod_db"
    },
    error_file: "/var/log/pm2/modelhub-backend-error.log",
    out_file: "/var/log/pm2/modelhub-backend-out.log",
    merge_logs: true
  }]
};
