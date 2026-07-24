"""
Schemas Pydantic pour Offer : DTO d entree/sortie.

OfferReview separe la decision de review (publish|reject) du reste,
pour que la route /offers/{id}/review n accepte que ce champ precis.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

from app.models.offer import OfferStatus


class OfferBase(BaseModel):
    title: str
    mission: str | None = None
    skills: str | None = None
    company_name: str | None = None


class OfferCreate(OfferBase):
    pass


class OfferRead(OfferBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: OfferStatus
    company_id: int
    created_at: datetime
    updated_at: datetime


class OfferReview(BaseModel):
    decision: Literal["publish", "reject"]
