from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.config import settings
from app.core.dependencies import DbSession, get_current_user
from app.models.user import User
from app.schemas.user_settings import UserSettingsResponse, UserSettingsUpdate
from app.services.user_settings_service import UserSettingsService

router = APIRouter(prefix="/config", tags=["config"])


@router.get("/cloudinary-config")
def cloudinary_config() -> dict[str, str]:
    """Devuelve el cloud name y upload preset de Cloudinary (público, sin auth)."""
    return {
        "cloud_name": settings.CLOUDINARY_CLOUD_NAME,
        "upload_preset": settings.CLOUDINARY_UPLOAD_PRESET,
    }


@router.get("/settings", response_model=UserSettingsResponse)
def get_settings(
    db: DbSession,
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserSettingsResponse:
    """Devuelve la configuración visual del usuario autenticado."""
    instance = UserSettingsService(db).get(current_user.id)
    return UserSettingsResponse.model_validate(instance)


@router.put("/settings", response_model=UserSettingsResponse)
def update_settings(
    payload: UserSettingsUpdate,
    db: DbSession,
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserSettingsResponse:
    """Actualiza la configuración visual del usuario autenticado."""
    instance = UserSettingsService(db).update(current_user.id, payload)
    return UserSettingsResponse.model_validate(instance)
