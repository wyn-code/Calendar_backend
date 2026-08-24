from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user_settings import UserSettings
from app.repositories.base import BaseRepository


class UserSettingsRepository(BaseRepository[UserSettings]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, UserSettings)

    def get_by_user_id(self, user_id: int) -> UserSettings | None:
        stmt = select(UserSettings).where(UserSettings.user_id == user_id)
        return self.db.scalars(stmt).first()

    def get_or_create(self, user_id: int) -> UserSettings:
        instance = self.get_by_user_id(user_id)
        if instance:
            return instance
        instance = UserSettings(user_id=user_id)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance
