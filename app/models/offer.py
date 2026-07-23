"""
Modele Offer : represente une offre de stage proposee par une entreprise.

Transitions de statut imposees par le sujet :
draft -> submitted -> published/rejected

Une offre ne peut etre publiee que si titre, mission, competences
et entreprise sont renseignes (regle verifiee au niveau repository/service,
pas au niveau du modele).
"""

import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class OfferStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    PUBLISHED = "published"
    REJECTED = "rejected"


class Offer(Base):
    __tablename__ = "offers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    mission: Mapped[str] = mapped_column(Text, nullable=True)
    skills: Mapped[str] = mapped_column(Text, nullable=True)
    company_name: Mapped[str] = mapped_column(String(255), nullable=True)

    status: Mapped[OfferStatus] = mapped_column(
        String(20), default=OfferStatus.DRAFT, nullable=False
    )

    # L'entreprise (User avec role=company) qui a cree l'offre
    company_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    applications: Mapped[list["Application"]] = relationship(
        back_populates="offer", cascade="all, delete-orphan"
    )
