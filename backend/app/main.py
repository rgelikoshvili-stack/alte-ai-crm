from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_system import router as system_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Alte AI CRM Chatbot",
    version=settings.APP_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(system_router)
