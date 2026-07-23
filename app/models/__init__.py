"""
Regroupe tous les modeles pour que SQLAlchemy resolve correctement
les relations entre eux (Offer <-> Application).
"""

from app.models.user import User
from app.models.offer import Offer
from app.models.application import Application

__all__ = ["User", "Offer", "Application"]
