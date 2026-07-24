"""
Schemas Pydantic pour Application : DTO d entree/sortie.

ApplicationDecision separe la decision (accepted|rejected) du reste,
pour que la route /applications/{id}/decision n accepte que ce champ precis.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

from app.models.application import ApplicationStatus


class ApplicationCreate(BaseModel):
    pass


class ApplicationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: ApplicationStatus
    offer_id: int
    student_id: int
    created_at: datetime
    updated_at: datetime


class ApplicationDecision(BaseModel):
    decision: Literal["accepted", "rejected"]
