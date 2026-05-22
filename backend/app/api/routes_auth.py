from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps_auth import get_current_user
from app.core.database import get_db
from app.models import User
from app.schemas.auth import CurrentUserResponse, LoginRequest, TokenResponse
from app.services.audit_service import audit_event
from app.services.security_service import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = (
        await db.scalars(
            select(User).where(User.email == payload.email.lower().strip())
        )
    ).first()
    if user is None or not user.is_active or not verify_password(payload.password, user.password_hash):
        await audit_event(
            db,
            action="login_failed",
            entity_type="user",
            entity_id=None,
            actor_type="anonymous",
            metadata_json={"email": payload.email.lower().strip()},
        )
        await db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(subject=user.id, role=user.role)
    await audit_event(
        db,
        action="login_succeeded",
        entity_type="user",
        entity_id=user.id,
        actor_type="user",
        actor_id=user.id,
    )
    await db.commit()
    await db.refresh(user)
    return TokenResponse(access_token=token, user=user)


@router.get("/me", response_model=CurrentUserResponse)
async def me(current_user: User = Depends(get_current_user)):
    return CurrentUserResponse(user=current_user)

