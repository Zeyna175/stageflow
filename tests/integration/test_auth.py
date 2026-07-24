"""
Tests d integration : authentification (register, login, /users/me).
"""

from tests.conftest import auth_headers


def test_register_creates_user(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "new@test.com",
            "full_name": "New User",
            "password": "test1234",
            "role": "student",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new@test.com"
    assert data["role"] == "student"
    assert "hashed_password" not in data


def test_register_duplicate_email_fails(client):
    payload = {
        "email": "dup@test.com",
        "full_name": "Dup User",
        "password": "test1234",
        "role": "student",
    }
    client.post("/auth/register", json=payload)
    response = client.post("/auth/register", json=payload)

    assert response.status_code == 400


def test_login_success_returns_token(client):
    client.post(
        "/auth/register",
        json={
            "email": "login@test.com",
            "full_name": "Login User",
            "password": "test1234",
            "role": "student",
        },
    )
    response = client.post(
        "/auth/login",
        data={"username": "login@test.com", "password": "test1234"},
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password_fails(client):
    client.post(
        "/auth/register",
        json={
            "email": "wrongpw@test.com",
            "full_name": "User",
            "password": "test1234",
            "role": "student",
        },
    )
    response = client.post(
        "/auth/login",
        data={"username": "wrongpw@test.com", "password": "bad_password"},
    )

    assert response.status_code == 401


def test_read_current_user_requires_auth(client):
    response = client.get("/users/me")
    assert response.status_code == 401


def test_read_current_user_returns_profile(client, student_token):
    response = client.get("/users/me", headers=auth_headers(student_token))
    assert response.status_code == 200
    assert response.json()["role"] == "student"
