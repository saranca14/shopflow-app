from pydantic import BaseModel, Field


class CartItem(BaseModel):
    product_id: int
    product_name: str = ""
    price: float = 0.0
    quantity: int = Field(..., ge=1)


class AddToCartRequest(BaseModel):
    product_id: int
    quantity: int = Field(default=1, ge=1)


class CartResponse(BaseModel):
    user_id: str
    items: list[CartItem]
    total_items: int
    total_price: float
