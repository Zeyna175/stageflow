"""
Repository pour Application : seul point d acces a la table applications.

Regles metier centralisees ici :
- Un etudiant ne peut avoir qu une candidature active (pending/accepted)
  par offre.
- Une candidature acceptee ne peut plus etre supprimee par l etudiant.
- Une entreprise ne peut jamais consulter les candidatures d une autre
  entreprise.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import BusinessRuleError, NotFoundError, PermissionDeniedError
from app.models.application import Application, ApplicationStatus
from app.models.offer import Offer, OfferStatus
from app.models.role import RoleName
from app.models.user import User


class ApplicationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, application_id: int) -> Application | None:
        return self.db.get(Application, application_id)

    def get_visible_by_id(self, application_id: int, current_user: User) -> Application:
        application = self.get_by_id(application_id)
        if application is None:
            raise NotFoundError("Candidature introuvable.")

        if (
            current_user.role == RoleName.STUDENT.value
            and application.student_id != current_user.id
        ):
            raise NotFoundError("Candidature introuvable.")

        if current_user.role == RoleName.COMPANY.value:
            offer = self.db.get(Offer, application.offer_id)
            if offer is None or offer.company_id != current_user.id:
                raise NotFoundError("Candidature introuvable.")

        return application

    def list_for_student(self, student: User) -> list[Application]:
        stmt = select(Application).where(Application.student_id == student.id)
        return list(self.db.execute(stmt).scalars().all())

    def list_for_offer(self, offer: Offer, current_user: User) -> list[Application]:
        """
        Une entreprise ne peut consulter que les candidatures de ses
        propres offres.
        """
        if current_user.role == RoleName.COMPANY.value and offer.company_id != current_user.id:
            raise PermissionDeniedError(
                "Vous ne pouvez consulter que les candidatures de vos propres offres."
            )

        stmt = select(Application).where(Application.offer_id == offer.id)
        return list(self.db.execute(stmt).scalars().all())

    def create(self, offer: Offer, student: User) -> Application:
        if offer.status != OfferStatus.PUBLISHED:
            raise BusinessRuleError("Impossible de postuler a une offre non publiee.")

        stmt = select(Application).where(
            Application.offer_id == offer.id,
            Application.student_id == student.id,
            Application.status.in_([ApplicationStatus.PENDING, ApplicationStatus.ACCEPTED]),
        )
        existing = self.db.execute(stmt).scalar_one_or_none()
        if existing is not None:
            raise BusinessRuleError("Vous avez deja une candidature active sur cette offre.")

        application = Application(
            offer_id=offer.id,
            student_id=student.id,
            status=ApplicationStatus.PENDING,
        )
        self.db.add(application)
        self.db.commit()
        self.db.refresh(application)
        return application

    def withdraw(self, application: Application, current_user: User) -> None:
        if application.student_id != current_user.id:
            raise PermissionDeniedError("Vous ne pouvez retirer que vos propres candidatures.")
        if application.status == ApplicationStatus.ACCEPTED:
            raise BusinessRuleError("Une candidature acceptee ne peut plus etre supprimee.")

        application.status = ApplicationStatus.WITHDRAWN
        self.db.commit()

    def decide(self, application: Application, decision: str) -> Application:
        if application.status != ApplicationStatus.PENDING:
            raise BusinessRuleError("Seule une candidature en attente peut recevoir une decision.")

        application.status = (
            ApplicationStatus.ACCEPTED if decision == "accepted" else ApplicationStatus.REJECTED
        )
        self.db.commit()
        self.db.refresh(application)
        return application
