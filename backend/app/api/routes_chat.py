from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import Conversation, Lead
from app.schemas.chat import ChatMessageRequest, ChatMessageResponse, ChatSessionStartRequest, ChatSessionStartResponse
from app.schemas.qualification import LeadQualificationResult
from app.services.chat_service import handle_message, request_handover, start_session

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/session/start", response_model=ChatSessionStartResponse)
async def start_chat_session(payload: ChatSessionStartRequest, db: AsyncSession = Depends(get_db)):
    return await start_session(db, payload)


@router.post("/message", response_model=ChatMessageResponse)
async def post_chat_message(payload: ChatMessageRequest, db: AsyncSession = Depends(get_db)):
    try:
        return await handle_message(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/handover/{conversation_id}")
async def request_chat_handover(conversation_id: str, db: AsyncSession = Depends(get_db)):
    try:
        return await request_handover(db, conversation_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/session/{conversation_id}/qualification", response_model=LeadQualificationResult)
async def get_chat_qualification(conversation_id: str, db: AsyncSession = Depends(get_db)):
    conversation = await db.get(Conversation, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if not conversation.lead_id:
        return LeadQualificationResult()
    lead = await db.get(Lead, conversation.lead_id)
    if lead is None:
        return LeadQualificationResult()
    return LeadQualificationResult(
        preferred_program=lead.program,
        intent=lead.qualification_intent or "unknown",
        urgency=lead.urgency or "low",
        language=conversation.language,
        lead_score=lead.lead_score or 10,
        qualification_status=lead.qualification_status or "new",
        handover_required=lead.handover_required,
        handover_reason=lead.handover_reason,
        recommended_next_action=lead.recommended_next_action or "ask_clarifying_question",
    )
