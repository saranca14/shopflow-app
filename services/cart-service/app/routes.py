from fastapi import APIRouter

from app.schemas import AddToCartRequest, CartResponse
from app import cart

router = APIRouter(prefix="/api/v1/cart", tags=["cart"])


@router.get("/{user_id}", response_model=CartResponse)
async def get_cart(user_id: str):
    """Get the contents of a user's cart."""
    cart_data = await cart.get_cart(user_id)
    items = cart_data.get("items", [])
    total_price = sum(i["price"] * i["quantity"] for i in items)
    total_items = sum(i["quantity"] for i in items)

    return CartResponse(
        user_id=user_id,
        items=items,
        total_items=total_items,
        total_price=round(total_price, 2),
    )


@router.post("/{user_id}/add", response_model=CartResponse)
async def add_to_cart(user_id: str, request: AddToCartRequest):
    """Add an item to the user's cart."""
    cart_data = await cart.add_item(user_id, request.product_id, request.quantity)
    items = cart_data.get("items", [])
    total_price = sum(i["price"] * i["quantity"] for i in items)
    total_items = sum(i["quantity"] for i in items)

    return CartResponse(
        user_id=user_id,
        items=items,
        total_items=total_items,
        total_price=round(total_price, 2),
    )


@router.delete("/{user_id}/remove/{product_id}", response_model=CartResponse)
async def remove_from_cart(user_id: str, product_id: int):
    """Remove an item from the user's cart."""
    cart_data = await cart.remove_item(user_id, product_id)
    items = cart_data.get("items", [])
    total_price = sum(i["price"] * i["quantity"] for i in items)
    total_items = sum(i["quantity"] for i in items)

    return CartResponse(
        user_id=user_id,
        items=items,
        total_items=total_items,
        total_price=round(total_price, 2),
    )


@router.delete("/{user_id}/clear", status_code=204)
async def clear_cart(user_id: str):
    """Clear the user's entire cart."""
    await cart.clear_cart(user_id)
