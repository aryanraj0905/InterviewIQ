from fastapi import FastAPI

from app.api.v1 import auth, health, users
from app.core.config import settings

app = FastAPI(title=settings.project_name, version=settings.version)

app.include_router(health.router, prefix=settings.api_v1_prefix)
app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(users.router, prefix=settings.api_v1_prefix)
