from fastapi import APIRouter

from app.api.routes import appointments, auth, export, health, obra_social, patients

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(patients.router)
api_router.include_router(appointments.router)
api_router.include_router(obra_social.router)
api_router.include_router(export.router)
