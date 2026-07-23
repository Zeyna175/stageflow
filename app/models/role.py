"""
Modele Role : represente les roles metier disponibles.

Roles : student, company, program_manager, admin
"""

import enum


class RoleName(str, enum.Enum):
    STUDENT = "student"
    COMPANY = "company"
    PROGRAM_MANAGER = "program_manager"
    ADMIN = "admin"
