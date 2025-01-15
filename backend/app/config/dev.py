class DevConfig:
    DATABASE_URL = "postgresql://twohun:twohun_password@localhost/twohun_db"
    CORS_ORIGINS = ["http://localhost:3000"]
    DEBUG = True
    RELOAD = True
    PORT = 8000
    HOST = "127.0.0.1"
    WORKERS = 1 