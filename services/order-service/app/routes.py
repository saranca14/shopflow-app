import logging
import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.config import settings
from app.database import get_db
from app.models import Order, OrderItem
from app.schemas import (
    CreateOrderRequest,
    UpdateOrderStatusRequest,
    OrderResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/orders", tags=["orders"])


@router.post("/", response_model=OrderResponse, status_code=201)
async def create_order(order_data: CreateOrderRequest, db: AsyncSession = Depends(get_db)):
    """Create a new order from the user's cart. Orchestrates cart → order → payment flow."""
    # 1. Fetch cart items from Cart Service
    cart_items = await _fetch_cart(order_data.user_id)
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    # 2. Create order
    total_amount = sum(item["price"] * item["quantity"] for item in cart_items)
    order = Order(
        user_id=order_data.user_id,
        status="pending",
        total_amount=round(total_amount, 2),
        shipping_address=order_data.shipping_address,
    )
    db.add(order)
    await db.flush()

    # 3. Create order items
    for item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item["product_id"],
            product_name=item.get("product_name", "Unknown"),
            quantity=item["quantity"],
            unit_price=item["price"],
            total_price=round(item["price"] * item["quantity"], 2),
        )
        db.add(order_item)

    await db.commit()

    # 4. Process payment
    order.status = "payment_processing"
    await db.commit()

    payment_result = await _process_payment(
        order_id=str(order.id),
        user_id=order_data.user_id,
        amount=order.total_amount,
    )

    if payment_result and payment_result.get("status") == "completed":
        order.status = "paid"
        order.payment_id = payment_result.get("payment_id")
    else:
        order.status = "payment_failed"

    await db.commit()

    # 5. Clear cart on successful payment
    if order.status == "paid":
        await _clear_cart(order_data.user_id)

    # Reload with items
    await db.refresh(order)
    result = await db.execute(
        select(Order).where(Order.id == order.id).options(selectinload(Order.items))
    )
    order = result.scalar_one()
    return order


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, db: AsyncSession = Depends(get_db)):
    """Get order details by ID."""
    result = await db.execute(
        select(Order).where(Order.id == order_id).options(selectinload(Order.items))
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.get("/user/{user_id}", response_model=list[OrderResponse])
async def get_user_orders(user_id: str, db: AsyncSession = Depends(get_db)):
    """Get all orders for a user."""
    result = await db.execute(
        select(Order)
        .where(Order.user_id == user_id)
        .options(selectinload(Order.items))
        .order_by(Order.created_at.desc())
    )
    orders = result.scalars().all()
    return orders


@router.put("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    status_data: UpdateOrderStatusRequest,
    db: AsyncSession = Depends(get_db),
):
    """Update order status."""
    result = await db.execute(
        select(Order).where(Order.id == order_id).options(selectinload(Order.items))
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = status_data.status.value
    await db.commit()
    await db.refresh(order)
    return order


# --- Inter-service communication helpers ---

async def _fetch_cart(user_id: str) -> list[dict]:
    """Fetch cart items from Cart Service."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{settings.CART_SERVICE_URL}/api/v1/cart/{user_id}")
            if resp.status_code == 200:
                data = resp.json()
                return data.get("items", [])
    except Exception as e:
        logger.error(f"Failed to fetch cart: {e}")
    return []


async def _process_payment(order_id: str, user_id: str, amount: float) -> dict:
    """Call Payment Service to process payment."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{settings.PAYMENT_SERVICE_URL}/api/v1/payments/process",
                json={
                    "order_id": order_id,
                    "user_id": user_id,
                    "amount": amount,
                    "currency": "USD",
                    "payment_method": "credit_card",
                },
            )
            if resp.status_code == 200:
                return resp.json()
    except Exception as e:
        logger.error(f"Failed to process payment: {e}")
    return None


async def _clear_cart(user_id: str):
    """Clear user's cart after successful order."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.delete(f"{settings.CART_SERVICE_URL}/api/v1/cart/{user_id}/clear")
    except Exception as e:
        logger.warning(f"Failed to clear cart: {e}")
