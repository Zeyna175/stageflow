"""
Permissions centralisees : dependances FastAPI pour authentification
et controle d acces par role.

Aucune route ne doit verifier un role directement ; elle doit dependre
de require_role(...) ou get_current_user.
"""

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.errors import NotAuthenticatedError, PermissionDeniedError
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.role import RoleName
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    if token is None:
        raise NotAuthenticatedError("Authentification requise.")

    payload = decode_access_token(token)
    if payload is None or "sub" not in payload:
        raise NotAuthenticatedError("Token invalide ou expire.")

    user = db.get(User, int(payload["sub"]))
    if user is None or not user.is_active:
        raise NotAuthenticatedError("Utilisateur introuvable ou inactif.")

    return user


def require_role(*allowed_roles: RoleName):
    """
    Fabrique une dependance FastAPI qui verifie que l utilisateur courant
    a l un des roles autorises.

    Usage : Depends(require_role(RoleName.ADMIN, RoleName.PROGRAM_MANAGER))
    """

    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in [r.value for r in allowed_roles]:
            raise PermissionDeniedError(
                "Vous n avez pas les droits necessaires pour cette action."
            )
        return current_user

    return dependency
