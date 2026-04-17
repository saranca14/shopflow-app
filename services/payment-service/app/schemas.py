from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentRequest(BaseModel):
    order_id: str
    user_id: str
    amount: float = Field(..., gt=0)
    currency: str = Field(default="USD", max_length=3)
    payment_method: str = Field(default="credit_card")


class PaymentResponse(BaseModel):
    payment_id: str
    order_id: str
    user_id: str
    amount: float
    currency: str
    status: PaymentStatus
    message: str
    processed_at: datetime
