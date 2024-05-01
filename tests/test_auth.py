import os

import pytest
from fastapi.testclient import TestClient

from api.app import app

os.environ["DB_HOST"] = "localhost:5439"


@pytest.fixture(scope="module")
def client():
    with TestClient(app=app) as c:
        yield c



def test_signup_for_access_token(client):
    response = client.post(
        "/api/v1/signup",
        json={
            "username": "latand",
            "password": "mysecretpassword",
            "full_name": "Latand",
        },
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_for_access_token(client):
    response = client.get(
        "/api/v1/token", params={"username": "latand", "password": "mysecretpassword"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_for_access_token_wrong_password(client):
    response = client.get(
        "/api/v1/token", params={"username": "latand", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert "detail" in response.json()


def test_login_for_access_token_no_username(client):
    response = client.get("/api/v1/token", params={"password": "mysecretpassword"})
    assert response.status_code == 422
    assert "detail" in response.json()
