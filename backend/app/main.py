from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.middleware import auth_rbac_middleware, correlation_middleware
from app.api.routes_analytics import router as analytics_router
from app.api.routes_auth import router as auth_router
from app.api.routes_chat import router as chat_router
from app.api.routes_conversations import router as conversations_router
from app.api.routes_customers import router as customers_router
from app.api.routes_dashboard import router as dashboard_router
from app.api.routes_deadlines import router as deadlines_router
from app.api.routes_departments import router as departments_router
from app.api.routes_inbox import router as inbox_router
from app.api.routes_knowledge import router as knowledge_router
from app.api.routes_leads import router as leads_router
from app.api.routes_pipelines import router as pipelines_router
from app.api.routes_system import router as system_router
from app.api.routes_tasks import router as tasks_router
from app.core.config import get_settings, validate_security_settings

settings = get_settings()
validate_security_settings(settings)

app = FastAPI(
    title="Alte AI CRM Chatbot",
    version=settings.APP_VERSION,
)

app.middleware("http")(correlation_middleware)
app.middleware("http")(auth_rbac_middleware)

# Keep CORS as the outermost user middleware for browser-visible error responses, including backend 500s.
# This lets failed chat requests still carry the exact allowed origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(system_router)
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(analytics_router)
app.include_router(dashboard_router)
app.include_router(departments_router)
app.include_router(customers_router)
app.include_router(pipelines_router)
app.include_router(leads_router)
app.include_router(conversations_router)
app.include_router(inbox_router)
app.include_router(knowledge_router)
app.include_router(tasks_router)
app.include_router(deadlines_router)
