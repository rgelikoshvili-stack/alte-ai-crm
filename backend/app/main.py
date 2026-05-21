from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_conversations import router as conversations_router
from app.api.routes_customers import router as customers_router
from app.api.routes_deadlines import router as deadlines_router
from app.api.routes_departments import router as departments_router
from app.api.routes_inbox import router as inbox_router
from app.api.routes_leads import router as leads_router
from app.api.routes_pipelines import router as pipelines_router
from app.api.routes_system import router as system_router
from app.api.routes_tasks import router as tasks_router
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
app.include_router(departments_router)
app.include_router(customers_router)
app.include_router(pipelines_router)
app.include_router(leads_router)
app.include_router(conversations_router)
app.include_router(inbox_router)
app.include_router(tasks_router)
app.include_router(deadlines_router)
