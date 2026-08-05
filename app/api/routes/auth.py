from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.dependencies import DbSession, get_current_user
from app.models.user import User
from app.schemas.auth import LoginResponse
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: DbSession) -> UserResponse:
    """Registra un nuevo usuario (stub)."""
    return AuthService(db).register(payload)


@router.post("/login", response_model=LoginResponse)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DbSession,
) -> LoginResponse:
    """Autentica con email y contraseña y devuelve un token JWT (stub)."""
    return AuthService(db).login(form_data.username, form_data.password)


@router.get("/me", response_model=UserResponse)
def me(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    """Devuelve el usuario autenticado."""
    return current_user
