from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session
from app.models import Product


SEED_PRODUCTS = [
    {
        "name": "Wireless Bluetooth Headphones",
        "description": "Premium noise-cancelling over-ear headphones with 30-hour battery life.",
        "price": 129.99,
        "category": "Electronics",
        "image_url": "https://placehold.co/400x400?text=Headphones",
        "stock_quantity": 150,
    },
    {
        "name": "Organic Cotton T-Shirt",
        "description": "Soft, breathable t-shirt made from 100% organic cotton. Available in multiple colors.",
        "price": 29.99,
        "category": "Clothing",
        "image_url": "https://placehold.co/400x400?text=T-Shirt",
        "stock_quantity": 500,
    },
    {
        "name": "Stainless Steel Water Bottle",
        "description": "Double-walled vacuum insulated bottle, keeps drinks cold 24hrs or hot 12hrs.",
        "price": 34.99,
        "category": "Home & Kitchen",
        "image_url": "https://placehold.co/400x400?text=Bottle",
        "stock_quantity": 300,
    },
    {
        "name": "Python Programming Book",
        "description": "Comprehensive guide to Python programming, from basics to advanced topics.",
        "price": 49.99,
        "category": "Books",
        "image_url": "https://placehold.co/400x400?text=Book",
        "stock_quantity": 200,
    },
    {
        "name": "Mechanical Keyboard",
        "description": "RGB backlit mechanical keyboard with Cherry MX switches and aluminum frame.",
        "price": 89.99,
        "category": "Electronics",
        "image_url": "https://placehold.co/400x400?text=Keyboard",
        "stock_quantity": 120,
    },
    {
        "name": "Running Shoes",
        "description": "Lightweight running shoes with responsive cushioning and breathable mesh upper.",
        "price": 119.99,
        "category": "Sports",
        "image_url": "https://placehold.co/400x400?text=Shoes",
        "stock_quantity": 250,
    },
    {
        "name": "Smart Watch",
        "description": "Fitness tracking smartwatch with heart rate monitor, GPS, and 7-day battery.",
        "price": 249.99,
        "category": "Electronics",
        "image_url": "https://placehold.co/400x400?text=SmartWatch",
        "stock_quantity": 80,
    },
    {
        "name": "Ceramic Coffee Mug Set",
        "description": "Set of 4 handcrafted ceramic mugs, microwave and dishwasher safe.",
        "price": 39.99,
        "category": "Home & Kitchen",
        "image_url": "https://placehold.co/400x400?text=Mugs",
        "stock_quantity": 400,
    },
    {
        "name": "Yoga Mat",
        "description": "Extra-thick non-slip yoga mat with carrying strap. 6mm cushioning.",
        "price": 45.99,
        "category": "Sports",
        "image_url": "https://placehold.co/400x400?text=YogaMat",
        "stock_quantity": 350,
    },
    {
        "name": "Wireless Charging Pad",
        "description": "Fast wireless charger compatible with all Qi-enabled devices. Sleek design.",
        "price": 24.99,
        "category": "Electronics",
        "image_url": "https://placehold.co/400x400?text=Charger",
        "stock_quantity": 600,
    },
    {
        "name": "Canvas Backpack",
        "description": "Durable canvas backpack with laptop compartment and multiple pockets.",
        "price": 59.99,
        "category": "Accessories",
        "image_url": "https://placehold.co/400x400?text=Backpack",
        "stock_quantity": 180,
    },
    {
        "name": "LED Desk Lamp",
        "description": "Adjustable LED desk lamp with 5 brightness levels and USB charging port.",
        "price": 42.99,
        "category": "Home & Kitchen",
        "image_url": "https://placehold.co/400x400?text=Lamp",
        "stock_quantity": 220,
    },
]


async def seed_products():
    """Seed the database with sample products if empty."""
    async with async_session() as session:
        from sqlalchemy import select, func

        count_result = await session.execute(select(func.count()).select_from(Product))
        count = count_result.scalar()

        if count == 0:
            for product_data in SEED_PRODUCTS:
                product = Product(**product_data)
                session.add(product)
            await session.commit()
            print(f"Seeded {len(SEED_PRODUCTS)} products.")
        else:
            print(f"Database already has {count} products. Skipping seed.")
