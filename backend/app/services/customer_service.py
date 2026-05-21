from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Customer
from app.schemas.crm import CustomerCreate
from app.services.audit_service import audit_event


async def create_or_update_customer(db: AsyncSession, payload: CustomerCreate) -> Customer:
    data = payload.model_dump()
    customer = None

    if payload.phone:
        customer = await db.scalar(select(Customer).where(Customer.phone == payload.phone))

    if customer is None and payload.email:
        customer = await db.scalar(select(Customer).where(Customer.email == payload.email))

    if customer is None:
        customer = Customer(**data)
        db.add(customer)
        await db.flush()
        await audit_event(db, action="customer_created", entity_type="customer", entity_id=customer.id)
    else:
        for field, value in data.items():
            if value is not None:
                setattr(customer, field, value)
        await db.flush()
        await audit_event(db, action="customer_updated", entity_type="customer", entity_id=customer.id)

    await db.commit()
    await db.refresh(customer)
    return customer
