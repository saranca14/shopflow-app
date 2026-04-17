import os


class Settings:
    APP_NAME: str = "Payment Service"
    APP_VERSION: str = "1.0.0"
    RABBITMQ_URL: str = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8005"))
    # Mock: success rate percentage
    PAYMENT_SUCCESS_RATE: int = int(os.getenv("PAYMENT_SUCCESS_RATE", "90"))


settings = Settings()
