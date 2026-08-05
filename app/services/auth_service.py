from sqlalchemy.orm import Session

from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginResponse
from app.schemas.user import UserCreate
from app.models.user import User


class AuthService:
    """Lógica de negocio de autenticación y registro (stub)."""

    def __init__(self, db: Session) -> None:
        self.repository = UserRepository(db)

    def register(self, data: UserCreate) -> User:
        """Registra un nuevo usuario."""
        raise NotImplementedError("Pendiente de implementación")

    def login(self, email: str, password: str) -> LoginResponse:
        """Autentica las credenciales y devuelve un token JWT."""
        raise NotImplementedError("Pendiente de implementación")
