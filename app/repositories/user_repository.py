from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repositorio de usuarios."""

    def __init__(self, db: Session) -> None:
        super().__init__(db, User)

    def get_by_email(self, email: str) -> User | None:
        """Busca un usuario por email (insensible a mayúsculas)."""
        stmt = select(User).where(func.lower(User.email) == email.lower())
        return self.db.scalars(stmt).first()
