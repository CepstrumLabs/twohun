class ProdConfig:
    DATABASE_URL = "postgresql://prod_user:prod_password@db/twohun_db"
    CORS_ORIGINS = ["https://yourdomain.com"]
    DEBUG = False
    RELOAD = False
    PORT = 8000
    HOST = "0.0.0.0"
    WORKERS = 4 