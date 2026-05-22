from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_or_404
from app.core.database import get_db
from app.models import Conversation, Message
from app.schemas.crm import ConversationCreate, ConversationRead, MessageCreate, MessageRead
from app.schemas.operator import ConversationDetail
from app.services.conversation_service import create_conversation, create_message

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("", response_model=ConversationRead)
async def create_conversation_route(payload: ConversationCreate, db: AsyncSession = Depends(get_db)):
    return await create_conversation(db, payload)


@router.get("/{conversation_id}", response_model=ConversationRead)
async def get_conversation(conversation_id: str, db: AsyncSession = Depends(get_db)):
    return await get_or_404(db, Conversation, conversation_id, "Conversation")


@router.get("/{conversation_id}/detail", response_model=ConversationDetail)
async def get_conversation_detail(conversation_id: str, db: AsyncSession = Depends(get_db)):
    conversation = await get_or_404(db, Conversation, conversation_id, "Conversation")
    from app.models import Customer, Lead

    customer = await db.get(Customer, conversation.customer_id) if conversation.customer_id else None
    lead = await db.get(Lead, conversation.lead_id) if conversation.lead_id else None
    messages = (
        await db.scalars(
            select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at.asc())
        )
    ).all()
    return ConversationDetail(
        conversation=conversation,
        customer=customer,
        lead=lead,
        messages=messages,
        summary=conversation.summary,
        human_handover=conversation.human_handover,
        ai_handled=conversation.ai_handled,
    )


@router.post("/{conversation_id}/messages", response_model=MessageRead)
async def create_message_route(
    conversation_id: str,
    payload: MessageCreate,
    db: AsyncSession = Depends(get_db),
):
    await get_or_404(db, Conversation, conversation_id, "Conversation")
    return await create_message(db, conversation_id, payload)


@router.get("/{conversation_id}/messages", response_model=list[MessageRead])
async def list_messages(conversation_id: str, db: AsyncSession = Depends(get_db)):
    await get_or_404(db, Conversation, conversation_id, "Conversation")
    query = select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at.asc())
    return (await db.scalars(query)).all()
