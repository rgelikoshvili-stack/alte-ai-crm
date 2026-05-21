from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_or_404
from app.core.database import get_db
from app.models import Customer
from app.schemas.crm import CustomerCreate, CustomerRead
from app.services.customer_service import create_or_update_customer

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("", response_model=CustomerRead)
async def create_customer(payload: CustomerCreate, db: AsyncSession = Depends(get_db)):
    return await create_or_update_customer(db, payload)


@router.get("/search", response_model=list[CustomerRead])
async def search_customers(
    phone: str | None = None,
    email: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Customer)
    if phone:
        query = query.where(Customer.phone == phone)
    if email:
        query = query.where(Customer.email == email)
    return (await db.scalars(query.order_by(Customer.created_at.desc()))).all()


@router.get("/{customer_id}", response_model=CustomerRead)
async def get_customer(customer_id: str, db: AsyncSession = Depends(get_db)):
    return await get_or_404(db, Customer, customer_id, "Customer")
