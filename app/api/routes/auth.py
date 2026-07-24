"""
Routes d authentification : /auth/register, /auth/login, /users/me.
"""

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.errors import BusinessRuleError, NotAuthenticatedError
from app.core.permissions import get_current_user
from app.core.security import create_access_token, verify_password
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import Token
from app.schemas.user import UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=201)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    repo = UserRepository(db)

    if repo.get_by_email(user_in.email) is not None:
        raise BusinessRuleError("Un compte existe deja avec cet email.")

    return repo.create(user_in)


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    repo = UserRepository(db)
    user = repo.get_by_email(form_data.username)

    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise NotAuthenticatedError("Email ou mot de passe incorrect.")

    token = create_access_token(subject=str(user.id), role=user.role)
    return Token(access_token=token)
