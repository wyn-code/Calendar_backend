from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base común para los schemas de respuesta (habilita `from_attributes`)."""

    model_config = ConfigDict(from_attributes=True)
