import os 
class ProdConfig:
    DATABASE_URL = os.getenv("DATABASE_URL")
    CORS_ORIGINS = os.getenv("CORS_ORIGINS")
    DEBUG = False
    RELOAD = False
    PORT = 8000
    HOST = "0.0.0.0"
    WORKERS = 1