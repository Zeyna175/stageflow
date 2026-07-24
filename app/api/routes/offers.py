"""
Routes Offer : creation, consultation, soumission et review des offres.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.permissions import get_current_user, require_role
from app.db.session import get_db
from app.models.role import RoleName
from app.models.user import User
from app.repositories.offer_repository import OfferRepository
from app.schemas.offer import OfferCreate, OfferRead, OfferReview

router = APIRouter(prefix="/offers", tags=["offers"])


@router.post("", response_model=OfferRead, status_code=201)
def create_offer(
    offer_in: OfferCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleName.COMPANY)),
):
    repo = OfferRepository(db)
    return repo.create(offer_in, current_user)


@router.get("", response_model=list[OfferRead])
def list_offers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = OfferRepository(db)
    return repo.list_for_user(current_user)


@router.get("/{offer_id}", response_model=OfferRead)
def get_offer(
    offer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = OfferRepository(db)
    return repo.get_visible_by_id(offer_id, current_user)


@router.patch("/{offer_id}/submit", response_model=OfferRead)
def submit_offer(
    offer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleName.COMPANY)),
):
    repo = OfferRepository(db)
    offer = repo.get_visible_by_id(offer_id, current_user)
    return repo.submit(offer, current_user)


@router.patch("/{offer_id}/review", response_model=OfferRead)
def review_offer(
    offer_id: int,
    review_in: OfferReview,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleName.PROGRAM_MANAGER)),
):
    repo = OfferRepository(db)
    offer = repo.get_visible_by_id(offer_id, current_user)
    return repo.review(offer, review_in.decision)
