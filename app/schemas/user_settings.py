from pydantic import Field

from app.schemas.base import BaseSchema


class UserSettingsResponse(BaseSchema):
    id: int
    user_id: int
    background_url: str | None = None
    primary_color: str | None = None


class UserSettingsUpdate(BaseSchema):
    background_url: str | None = Field(default=None, max_length=2000)
    primary_color: str | None = Field(default=None, max_length=7)
