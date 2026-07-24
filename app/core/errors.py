"""
Exceptions metier centralisees.

- 400 : regle metier invalide
- 401 : non authentifie
- 403 : non habilite
- 404 : ressource absente ou non visible
"""


class AppError(Exception):
    status_code: int = 400

    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)


class BusinessRuleError(AppError):
    status_code = 400


class NotAuthenticatedError(AppError):
    status_code = 401


class PermissionDeniedError(AppError):
    status_code = 403


class NotFoundError(AppError):
    status_code = 404