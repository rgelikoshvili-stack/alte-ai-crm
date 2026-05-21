from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.chat import ChatMessageRequest, ChatMessageResponse, ChatSessionStartRequest, ChatSessionStartResponse
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
