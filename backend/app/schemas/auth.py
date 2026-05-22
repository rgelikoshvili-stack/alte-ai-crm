from pydantic import BaseModel

from app.schemas.crm import UserRead


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead


class CurrentUserResponse(BaseModel):
    user: UserRead
