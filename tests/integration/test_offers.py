"""
Tests d integration : offres (workflow, permissions, invariants).
"""

from tests.conftest import auth_headers


def _create_offer(client, token):
    return client.post(
        "/offers",
        json={
            "title": "Stage Data Analyst",
            "mission": "Analyse de donnees",
            "skills": "Python, SQL",
            "company_name": "TestCorp",
        },
        headers=auth_headers(token),
    )


def test_company_can_create_offer(client, company_token):
    response = _create_offer(client, company_token)
    assert response.status_code == 201
    assert response.json()["status"] == "draft"


def test_student_cannot_create_offer(client, student_token):
    response = _create_offer(client, student_token)
    assert response.status_code == 403


def test_create_offer_requires_auth(client):
    response = client.post("/offers", json={"title": "X"})
    assert response.status_code == 401


def test_full_offer_workflow_draft_to_published(client, company_token, manager_token):
    offer = _create_offer(client, company_token).json()
    offer_id = offer["id"]

    submit_response = client.patch(
        f"/offers/{offer_id}/submit", headers=auth_headers(company_token)
    )
    assert submit_response.status_code == 200
    assert submit_response.json()["status"] == "submitted"

    review_response = client.patch(
        f"/offers/{offer_id}/review",
        json={"decision": "publish"},
        headers=auth_headers(manager_token),
    )
    assert review_response.status_code == 200
    assert review_response.json()["status"] == "published"


def test_offer_review_requires_program_manager_role(client, company_token):
    offer = _create_offer(client, company_token).json()
    offer_id = offer["id"]
    client.patch(f"/offers/{offer_id}/submit", headers=auth_headers(company_token))

    response = client.patch(
        f"/offers/{offer_id}/review",
        json={"decision": "publish"},
        headers=auth_headers(company_token),
    )
    assert response.status_code == 403


def test_cannot_review_offer_still_in_draft(client, company_token, manager_token):
    offer = _create_offer(client, company_token).json()
    offer_id = offer["id"]

    response = client.patch(
        f"/offers/{offer_id}/review",
        json={"decision": "publish"},
        headers=auth_headers(manager_token),
    )
    assert response.status_code == 400


def test_company_cannot_access_another_companys_offer(client, company_token):
    offer = _create_offer(client, company_token).json()
    offer_id = offer["id"]

    other_company_response = client.post(
        "/auth/register",
        json={
            "email": "other_company@test.com",
            "full_name": "Other Company",
            "password": "test1234",
            "role": "company",
        },
    )
    assert other_company_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        data={"username": "other_company@test.com", "password": "test1234"},
    )
    other_token = login_response.json()["access_token"]

    response = client.get(f"/offers/{offer_id}", headers=auth_headers(other_token))
    assert response.status_code == 404


def test_student_cannot_see_draft_offer(client, company_token, student_token):
    offer = _create_offer(client, company_token).json()
    offer_id = offer["id"]

    response = client.get(f"/offers/{offer_id}", headers=auth_headers(student_token))
    assert response.status_code == 404


def test_student_can_see_published_offer(client, company_token, manager_token, student_token):
    offer = _create_offer(client, company_token).json()
    offer_id = offer["id"]
    client.patch(f"/offers/{offer_id}/submit", headers=auth_headers(company_token))
    client.patch(
        f"/offers/{offer_id}/review",
        json={"decision": "publish"},
        headers=auth_headers(manager_token),
    )

    response = client.get(f"/offers/{offer_id}", headers=auth_headers(student_token))
    assert response.status_code == 200
    assert response.json()["status"] == "published"
