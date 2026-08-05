from pydantic import BaseModel

from app.schemas.user import UserResponse


class LoginRequest(BaseModel):
    """Cuerpo de login (JSON) con email y contraseña.

    `remember_me` amplía la validez del token para mantener la sesión iniciada.
    """

    email: str
    password: str
    remember_me: bool = False


class Token(BaseModel):
    """Token JWT devuelto tras un login exitoso."""

    access_token: str
    token_type: str = "bearer"


class LoginResponse(Token):
    """Respuesta de login: token JWT + datos del usuario."""

    user: UserResponse
