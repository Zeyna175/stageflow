"""
Tests d integration : candidatures (creation, invariants, isolation,
decisions).
"""

from tests.conftest import auth_headers


def _create_and_publish_offer(client, company_token, manager_token):
    offer = client.post(
        "/offers",
        json={
            "title": "Stage Data Analyst",
            "mission": "Analyse de donnees",
            "skills": "Python, SQL",
            "company_name": "TestCorp",
        },
        headers=auth_headers(company_token),
    ).json()
    offer_id = offer["id"]

    client.patch(f"/offers/{offer_id}/submit", headers=auth_headers(company_token))
    client.patch(
        f"/offers/{offer_id}/review",
        json={"decision": "publish"},
        headers=auth_headers(manager_token),
    )
    return offer_id


def test_student_can_apply_to_published_offer(client, company_token, manager_token, student_token):
    offer_id = _create_and_publish_offer(client, company_token, manager_token)

    response = client.post(
        f"/offers/{offer_id}/applications", headers=auth_headers(student_token)
    )
    assert response.status_code == 201
    assert response.json()["status"] == "pending"


def test_cannot_apply_to_unpublished_offer(client, company_token, student_token):
    offer = client.post(
        "/offers",
        json={
            "title": "Stage Draft",
            "mission": "Mission",
            "skills": "Skills",
            "company_name": "TestCorp",
        },
        headers=auth_headers(company_token),
    ).json()

    response = client.post(
        f"/offers/{offer['id']}/applications", headers=auth_headers(student_token)
    )
    assert response.status_code == 404


def test_student_cannot_have_two_active_applications_on_same_offer(
    client, company_token, manager_token, student_token
):
    offer_id = _create_and_publish_offer(client, company_token, manager_token)

    first = client.post(f"/offers/{offer_id}/applications", headers=auth_headers(student_token))
    assert first.status_code == 201

    second = client.post(f"/offers/{offer_id}/applications", headers=auth_headers(student_token))
    assert second.status_code == 400


def test_company_cannot_access_other_companys_offer_applications(
    client, company_token, manager_token, student_token
):
    """
    Test d isolation explicitement demande par le sujet : une entreprise
    tente d acceder aux candidatures d une offre qui ne lui appartient pas.
    """
    offer_id = _create_and_publish_offer(client, company_token, manager_token)
    client.post(f"/offers/{offer_id}/applications", headers=auth_headers(student_token))

    other_company = client.post(
        "/auth/register",
        json={
            "email": "intruder@test.com",
            "full_name": "Intruder Company",
            "password": "test1234",
            "role": "company",
        },
    )
    assert other_company.status_code == 201

    login = client.post(
        "/auth/login",
        data={"username": "intruder@test.com", "password": "test1234"},
    )
    other_token = login.json()["access_token"]

    response = client.get(
        f"/offers/{offer_id}/applications", headers=auth_headers(other_token)
    )
    assert response.status_code == 404


def test_manager_can_accept_application(
    client, company_token, manager_token, student_token
):
    offer_id = _create_and_publish_offer(client, company_token, manager_token)
    application = client.post(
        f"/offers/{offer_id}/applications", headers=auth_headers(student_token)
    ).json()

    response = client.patch(
        f"/applications/{application['id']}/decision",
        json={"decision": "accepted"},
        headers=auth_headers(manager_token),
    )
    assert response.status_code == 200
    assert response.json()["status"] == "accepted"


def test_student_cannot_withdraw_accepted_application(
    client, company_token, manager_token, student_token
):
    offer_id = _create_and_publish_offer(client, company_token, manager_token)
    application = client.post(
        f"/offers/{offer_id}/applications", headers=auth_headers(student_token)
    ).json()
    client.patch(
        f"/applications/{application['id']}/decision",
        json={"decision": "accepted"},
        headers=auth_headers(manager_token),
    )

    response = client.delete(
        f"/applications/{application['id']}", headers=auth_headers(student_token)
    )
    assert response.status_code == 400


def test_student_can_withdraw_pending_application(
    client, company_token, manager_token, student_token
):
    offer_id = _create_and_publish_offer(client, company_token, manager_token)
    application = client.post(
        f"/offers/{offer_id}/applications", headers=auth_headers(student_token)
    ).json()

    response = client.delete(
        f"/applications/{application['id']}", headers=auth_headers(student_token)
    )
    assert response.status_code == 204
