from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import Conversation, Customer, Lead, Message
from app.schemas.crm import InboxItem

router = APIRouter(prefix="/inbox", tags=["inbox"])


@router.get("", response_model=list[InboxItem])
async def list_inbox(db: AsyncSession = Depends(get_db)):
    conversations = (await db.scalars(select(Conversation).order_by(Conversation.created_at.desc()))).all()
    items = []
    for conversation in conversations:
        customer = await db.get(Customer, conversation.customer_id) if conversation.customer_id else None
        lead = await db.get(Lead, conversation.lead_id) if conversation.lead_id else None
        last_message = await db.scalar(
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(Message.created_at.desc())
            .limit(1)
        )
        items.append(
            {
                "conversation": conversation,
                "customer": customer,
                "lead": lead,
                "last_message": last_message,
            }
        )
    return items
