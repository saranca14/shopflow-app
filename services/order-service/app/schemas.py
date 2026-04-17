from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class OrderStatus(str, Enum):
    PENDING = "pending"
    PAYMENT_PROCESSING = "payment_processing"
    PAID = "paid"
    PAYMENT_FAILED = "payment_failed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    quantity: int
    unit_price: float
    total_price: float

    class Config:
        from_attributes = True


class CreateOrderRequest(BaseModel):
    user_id: str
    shipping_address: Optional[str] = None


class UpdateOrderStatusRequest(BaseModel):
    status: OrderStatus


class OrderResponse(BaseModel):
    id: int
    user_id: str
    status: str
    total_amount: float
    shipping_address: Optional[str] = None
    payment_id: Optional[str] = None
    items: list[OrderItemResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
