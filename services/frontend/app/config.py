import os


class Config:
    APP_NAME = "ShopFlow"
    SECRET_KEY = os.getenv("SECRET_KEY", "frontend-secret-key-change-me")
    PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8001")
    CART_SERVICE_URL = os.getenv("CART_SERVICE_URL", "http://localhost:8002")
    ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL", "http://localhost:8003")
    USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8004")
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "5000"))
