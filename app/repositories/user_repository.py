"""
Repository pour User : seul point d acces a la table users.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return self.db.execute(stmt).scalar_one_or_none()

    def create(self, user_in: UserCreate) -> User:
        user = User(
            email=user_in.email,
            full_name=user_in.full_name,
            hashed_password=hash_password(user_in.password),
            role=user_in.role.value,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
