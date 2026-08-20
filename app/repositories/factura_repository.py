from sqlalchemy.orm import Session

from app.models.config_models import Factura
from app.repositories.base import BaseRepository


class FacturaRepository(BaseRepository[Factura]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, Factura)
