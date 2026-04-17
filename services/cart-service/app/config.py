import os


class Settings:
    APP_NAME: str = "Cart Service"
    APP_VERSION: str = "1.0.0"
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    PRODUCT_SERVICE_URL: str = os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8001")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8002"))


settings = Settings()
