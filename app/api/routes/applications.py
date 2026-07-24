"""
Routes Application : candidature, consultation, retrait et decision.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.permissions import get_current_user, require_role
from app.db.session import get_db
from app.models.role import RoleName
from app.models.user import User
from app.repositories.application_repository import ApplicationRepository
from app.repositories.offer_repository import OfferRepository
from app.schemas.application import ApplicationDecision, ApplicationRead

router = APIRouter(tags=["applications"])


@router.post("/offers/{offer_id}/applications", response_model=ApplicationRead, status_code=201)
def create_application(
    offer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleName.STUDENT)),
):
    offer_repo = OfferRepository(db)
    application_repo = ApplicationRepository(db)

    offer = offer_repo.get_visible_by_id(offer_id, current_user)
    return application_repo.create(offer, current_user)


@router.get("/applications/me", response_model=list[ApplicationRead])
def list_my_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleName.STUDENT)),
):
    repo = ApplicationRepository(db)
    return repo.list_for_student(current_user)


@router.get("/offers/{offer_id}/applications", response_model=list[ApplicationRead])
def list_offer_applications(
    offer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(RoleName.COMPANY, RoleName.PROGRAM_MANAGER, RoleName.ADMIN)
    ),
):
    offer_repo = OfferRepository(db)
    application_repo = ApplicationRepository(db)

    offer = offer_repo.get_visible_by_id(offer_id, current_user)
    return application_repo.list_for_offer(offer, current_user)


@router.patch("/applications/{application_id}/decision", response_model=ApplicationRead)
def decide_application(
    application_id: int,
    decision_in: ApplicationDecision,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleName.PROGRAM_MANAGER)),
):
    repo = ApplicationRepository(db)
    application = repo.get_visible_by_id(application_id, current_user)
    return repo.decide(application, decision_in.decision)


@router.delete("/applications/{application_id}", status_code=204)
def withdraw_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleName.STUDENT)),
):
    repo = ApplicationRepository(db)
    application = repo.get_visible_by_id(application_id, current_user)
    repo.withdraw(application, current_user)
