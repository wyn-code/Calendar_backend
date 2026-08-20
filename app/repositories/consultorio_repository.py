from sqlalchemy.orm import Session

from app.models.consultorio import Consultorio
from app.repositories.base import BaseRepository


class ConsultorioRepository(BaseRepository[Consultorio]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, Consultorio)
