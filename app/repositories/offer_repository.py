"""
Repository pour Offer : seul point d acces a la table offers.

Regles metier centralisees ici :
- Une offre ne peut etre publiee que si titre, mission, competences
  et entreprise sont renseignes.
- Transition explicite : draft -> submitted -> published/rejected.
- Une entreprise ne peut jamais consulter/modifier les offres d une
  autre entreprise.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import BusinessRuleError, NotFoundError, PermissionDeniedError
from app.models.offer import Offer, OfferStatus
from app.models.role import RoleName
from app.models.user import User
from app.schemas.offer import OfferCreate


class OfferRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, offer_id: int) -> Offer | None:
        return self.db.get(Offer, offer_id)

    def get_visible_by_id(self, offer_id: int, current_user: User) -> Offer:
        """
        404 si l offre n existe pas OU n est pas visible par l utilisateur
        (on ne distingue pas les deux cas, pour ne pas fuiter d information).
        """
        offer = self.get_by_id(offer_id)
        if offer is None:
            raise NotFoundError("Offre introuvable.")

        if current_user.role == RoleName.COMPANY.value and offer.company_id != current_user.id:
            raise NotFoundError("Offre introuvable.")

        if current_user.role == RoleName.STUDENT.value and offer.status != OfferStatus.PUBLISHED:
            raise NotFoundError("Offre introuvable.")

        return offer

    def list_for_user(self, current_user: User) -> list[Offer]:
        stmt = select(Offer)

        if current_user.role == RoleName.STUDENT.value:
            stmt = stmt.where(Offer.status == OfferStatus.PUBLISHED)
        elif current_user.role == RoleName.COMPANY.value:
            stmt = stmt.where(Offer.company_id == current_user.id)
        # program_manager et admin voient tout

        return list(self.db.execute(stmt).scalars().all())

    def create(self, offer_in: OfferCreate, company_user: User) -> Offer:
        offer = Offer(
            title=offer_in.title,
            mission=offer_in.mission,
            skills=offer_in.skills,
            company_name=offer_in.company_name,
            company_id=company_user.id,
            status=OfferStatus.DRAFT,
        )
        self.db.add(offer)
        self.db.commit()
        self.db.refresh(offer)
        return offer

    def submit(self, offer: Offer, current_user: User) -> Offer:
        if offer.company_id != current_user.id:
            raise PermissionDeniedError("Vous ne pouvez soumettre que vos propres offres.")
        if offer.status != OfferStatus.DRAFT:
            raise BusinessRuleError("Seule une offre en brouillon peut etre soumise.")

        offer.status = OfferStatus.SUBMITTED
        self.db.commit()
        self.db.refresh(offer)
        return offer

    def review(self, offer: Offer, decision: str) -> Offer:
        if offer.status != OfferStatus.SUBMITTED:
            raise BusinessRuleError("Seule une offre soumise peut etre revue.")

        if decision == "publish":
            if not offer.title or not offer.mission or not offer.skills or not offer.company_name:
                raise BusinessRuleError(
                    "Titre, mission, competences et entreprise sont requis pour publier."
                )
            offer.status = OfferStatus.PUBLISHED
        else:
            offer.status = OfferStatus.REJECTED

        self.db.commit()
        self.db.refresh(offer)
        return offer
