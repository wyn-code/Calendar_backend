from sqlalchemy.orm import Session

from app.models.obra_social import ObraSocial
from app.repositories.base import BaseRepository


class ObraSocialRepository(BaseRepository[ObraSocial]):
    """Repositorio de obras sociales."""

    def __init__(self, db: Session) -> None:
        super().__init__(db, ObraSocial)
