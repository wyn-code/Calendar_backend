from fastapi import APIRouter

from app.api.routes import (
    appointments,
    auth,
    billing,
    billing_por_consultorio,
    consultorios,
    config,
    export,
    facturas,
    health,
    obra_social,
    patients,
    patients_summary,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(patients_summary.router)
api_router.include_router(patients.router)
api_router.include_router(appointments.router)
api_router.include_router(obra_social.router)
api_router.include_router(export.router)
api_router.include_router(billing.router)
api_router.include_router(billing_por_consultorio.router)
api_router.include_router(consultorios.router)
api_router.include_router(config.router)
api_router.include_router(facturas.router)
