from sqlalchemy.orm import Session

from app.models.user_settings import UserSettings
from app.repositories.user_settings_repository import UserSettingsRepository
from app.schemas.user_settings import UserSettingsUpdate


class UserSettingsService:
    def __init__(self, db: Session) -> None:
        self.repo = UserSettingsRepository(db)

    def get(self, user_id: int) -> UserSettings:
        return self.repo.get_or_create(user_id)

    def update(self, user_id: int, data: UserSettingsUpdate) -> UserSettings:
        instance = self.repo.get_or_create(user_id)
        return self.repo.update(instance, data)
