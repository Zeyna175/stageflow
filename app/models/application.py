"""
Modele Application : represente la candidature d'un etudiant a une offre.

Transitions de statut imposees par le sujet :
pending -> accepted/rejected/withdrawn

Invariants metier (verifies au niveau repository/service) :
- Un etudiant ne peut avoir qu'une candidature active (pending/accepted)
  par offre.
- Une candidature acceptee ne peut plus etre supprimee par l'etudiant.
"""

import enum
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.offer import Offer


class ApplicationStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (
        UniqueConstraint("offer_id", "student_id", name="uq_application_offer_student"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    status: Mapped[ApplicationStatus] = mapped_column(
        String(20), default=ApplicationStatus.PENDING, nullable=False
    )

    offer_id: Mapped[int] = mapped_column(ForeignKey("offers.id"), nullable=False)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    offer: Mapped["Offer"] = relationship(back_populates="applications")