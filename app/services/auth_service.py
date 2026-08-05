from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginResponse
from app.schemas.user import UserCreate, UserResponse


class AuthService:
    """Lógica de negocio de autenticación."""

    def __init__(self, db: Session) -> None:
        self.repository = UserRepository(db)

    def register(self, data: UserCreate) -> User:
        """Registra un nuevo usuario si el email no está en uso."""
        if self.repository.get_by_email(data.email) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un usuario con ese email",
            )
        user = User(
            email=data.email,
            password_hash=hash_password(data.password),
            nombre=data.nombre,
        )
        self.repository.db.add(user)
        self.repository.db.commit()
        self.repository.db.refresh(user)
        return user

    def login(self, email: str, password: str, remember_me: bool = False) -> LoginResponse:
        """Autentica las credenciales y devuelve un token JWT."""
        user = self.repository.get_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.activo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario deshabilitado",
            )

        expires_minutes = (
            settings.REMEMBER_ME_EXPIRE_DAYS * 24 * 60
            if remember_me
            else settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        access_token = create_access_token(
            subject=str(user.id), expires_minutes=expires_minutes
        )

        return LoginResponse(
            access_token=access_token,
            user=UserResponse.model_validate(user),
        )
