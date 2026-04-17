import json
import httpx
import redis.asyncio as redis

from app.config import settings

redis_client: redis.Redis = None


async def get_redis() -> redis.Redis:
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return redis_client


def _cart_key(user_id: str) -> str:
    return f"cart:{user_id}"


async def get_cart(user_id: str) -> dict:
    """Get all items in the user's cart."""
    r = await get_redis()
    cart_data = await r.get(_cart_key(user_id))
    if cart_data:
        return json.loads(cart_data)
    return {"items": []}


async def add_item(user_id: str, product_id: int, quantity: int) -> dict:
    """Add/update an item in the cart. Fetches product details from Product Service."""
    r = await get_redis()
    cart = await get_cart(user_id)
    items = cart.get("items", [])

    # Fetch product info from product service
    product_info = await _fetch_product(product_id)

    # Check if item already exists
    existing = next((i for i in items if i["product_id"] == product_id), None)
    if existing:
        existing["quantity"] += quantity
        existing["price"] = product_info.get("price", existing["price"])
        existing["product_name"] = product_info.get("name", existing["product_name"])
    else:
        items.append({
            "product_id": product_id,
            "product_name": product_info.get("name", "Unknown"),
            "price": product_info.get("price", 0.0),
            "quantity": quantity,
        })

    cart["items"] = items
    await r.set(_cart_key(user_id), json.dumps(cart), ex=86400)  # 24h TTL
    return cart


async def remove_item(user_id: str, product_id: int) -> dict:
    """Remove an item from the cart."""
    r = await get_redis()
    cart = await get_cart(user_id)
    cart["items"] = [i for i in cart.get("items", []) if i["product_id"] != product_id]
    await r.set(_cart_key(user_id), json.dumps(cart), ex=86400)
    return cart


async def clear_cart(user_id: str):
    """Clear the entire cart."""
    r = await get_redis()
    await r.delete(_cart_key(user_id))


async def _fetch_product(product_id: int) -> dict:
    """Fetch product details from Product Service."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                f"{settings.PRODUCT_SERVICE_URL}/api/v1/products/{product_id}"
            )
            if resp.status_code == 200:
                return resp.json()
    except Exception:
        pass
    return {"name": "Unknown Product", "price": 0.0}
