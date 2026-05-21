from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Conversation, Message
from app.schemas.crm import ConversationCreate, MessageCreate
from app.services.audit_service import audit_event


async def create_conversation(db: AsyncSession, payload: ConversationCreate) -> Conversation:
    conversation = Conversation(**payload.model_dump())
    db.add(conversation)
    await db.flush()
    await audit_event(
        db,
        action="conversation_created",
        entity_type="conversation",
        entity_id=conversation.id,
    )
    await db.commit()
    await db.refresh(conversation)
    return conversation


async def create_message(db: AsyncSession, conversation_id: str, payload: MessageCreate) -> Message:
    message = Message(conversation_id=conversation_id, **payload.model_dump())
    db.add(message)
    await db.flush()
    await audit_event(
        db,
        action="message_received",
        entity_type="message",
        entity_id=message.id,
        metadata_json={"conversation_id": conversation_id, "sender_type": message.sender_type},
    )
    await db.commit()
    await db.refresh(message)
    return message
