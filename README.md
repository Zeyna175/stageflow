# StageFlow -- API de gestion securisee des stages data

API interne developpee avec FastAPI pour gerer les offres de stage, les
candidatures, les validations pedagogiques et les avis des encadrants,
avec un controle d acces strict par role.

## Stack technique

- FastAPI + Pydantic v2
- SQLAlchemy 2.0 + Alembic (migrations)
- PostgreSQL (production) / SQLite en memoire (tests)
- JWT (OAuth2 password flow) + bcrypt
- Docker + docker-compose
- pytest + pytest-cov, CI GitHub Actions + Codecov

## Roles et permissions

| Role | Droits |
|---|---|
| student | Consulte les offres publiees, postule, retire sa candidature (si non acceptee) |
| company | Cree/soumet ses offres, consulte les candidatures de ses propres offres |
| program_manager | Publie/refuse une offre, decide des candidatures |
| admin | Gere les utilisateurs (a etendre) |

## Installation locale

### Prerequis
- Python 3.12
- Docker Desktop

### 1. Cloner et installer les dependances

```powershell
git clone https://github.com/Zeyna175/stageflow.git
cd stageflow
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. Variables d environnement

Copier .env.example en .env et ajuster si besoin :

```powershell
Copy-Item .env.example .env
```

### 3. Lancer la base de donnees

```powershell
docker compose up -d db
```

### 4. Appliquer les migrations

```powershell
alembic upgrade head
```

### 5. Lancer l API en local

```powershell
uvicorn app.main:app --reload
```

L API est disponible sur http://127.0.0.1:8000, la documentation
interactive sur http://127.0.0.1:8000/docs.

## Lancer avec Docker Compose (application + base de donnees)

```powershell
docker compose up -d --build
```

## Lancer les tests

```powershell
pytest -v
```

Avec couverture :

```powershell
pytest --cov=app --cov-report=term-missing
```

## Structure du projet

app/
main.py Point d entree FastAPI
api/routes/ Routes HTTP (auth, users, offers, applications)
core/ Configuration, securite, permissions, erreurs
db/ Session et base SQLAlchemy
models/ Modeles SQLAlchemy
schemas/ Schemas Pydantic (DTO entree/sortie)
repositories/ Acces aux donnees (aucune route n appelle SQLAlchemy directement)
middlewares/ request_id, security_headers
tests/
unit/
integration/ Tests des routes (auth, offers, applications)


## Endpoints principaux

- POST /auth/register, POST /auth/login, GET /users/me
- POST /offers, GET /offers, GET /offers/{id}, PATCH /offers/{id}/submit
- PATCH /offers/{id}/review (decision publish ou reject)
- POST /offers/{id}/applications, GET /applications/me, GET /offers/{id}/applications
- PATCH /applications/{id}/decision, DELETE /applications/{id}

## CI/CD

Le pipeline GitHub Actions (.github/workflows/ci.yml) execute a chaque
push/pull request sur main :
1. Installation des dependances
2. Lancement des tests avec couverture
3. Upload du rapport de couverture vers Codecov
4. Build de l image Docker (publiee sur GitHub Container Registry)
