from pydantic import BaseModel

from app.schemas.user import UserResponse


class LoginRequest(BaseModel):
    """Cuerpo de login alternativo (JSON). El flujo OAuth2 usa form-data."""

    email: str
    password: str


class Token(BaseModel):
    """Token JWT devuelto tras un login exitoso."""

    access_token: str
    token_type: str = "bearer"


class LoginResponse(Token):
    """Respuesta de login: token JWT + datos del usuario."""

    user: UserResponse
