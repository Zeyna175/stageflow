"""
Schemas Pydantic pour User : DTO d entree/sortie.

UserRead ne doit jamais exposer hashed_password.
"""

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.role import RoleName


class UserBase(BaseModel):
    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    password: str
    role: RoleName


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: RoleName
    is_active: bool
