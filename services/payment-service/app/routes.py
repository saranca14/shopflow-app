import random
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter

from app.config import settings
from app.schemas import PaymentRequest, PaymentResponse, PaymentStatus
from app.events import publish_payment_event

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])

# In-memory store for simplicity (would be a DB in production)
payments_store: dict[str, dict] = {}


@router.post("/process", response_model=PaymentResponse)
async def process_payment(payment: PaymentRequest):
    """Process a payment (mock). Simulates success/failure based on configured rate."""
    payment_id = str(uuid.uuid4())
    is_success = random.randint(1, 100) <= settings.PAYMENT_SUCCESS_RATE

    status = PaymentStatus.COMPLETED if is_success else PaymentStatus.FAILED
    message = "Payment processed successfully" if is_success else "Payment declined by processor"

    result = {
        "payment_id": payment_id,
        "order_id": payment.order_id,
        "user_id": payment.user_id,
        "amount": payment.amount,
        "currency": payment.currency,
        "status": status,
        "message": message,
        "processed_at": datetime.now(timezone.utc),
    }

    payments_store[payment_id] = result

    # Publish event to RabbitMQ
    try:
        publish_payment_event(
            event_type=status.value,
            data={
                "payment_id": payment_id,
                "order_id": payment.order_id,
                "user_id": payment.user_id,
                "amount": payment.amount,
                "status": status.value,
            },
        )
    except Exception:
        pass  # Non-critical: event publishing failure shouldn't break payment

    return PaymentResponse(**result)


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(payment_id: str):
    """Get payment status by ID."""
    payment = payments_store.get(payment_id)
    if not payment:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Payment not found")
    return PaymentResponse(**payment)
