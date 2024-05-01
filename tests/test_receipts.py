import asyncio
from fastapi.testclient import TestClient
import pytest
from api.app import app
import os


os.environ["DB_HOST"] = "localhost:5439"
os.environ["TESING"] = "1"

valid_product = {
    "name": "Product 1",
    "price": "10.50",
    "quantity": "2.5",
    "comment": "Sample comment",
}

invalid_product = {
    "name": "Product 2",
    "price": "10.50",
    "quantity": "-2.5",
    "comment": None,
}

valid_payment = {
    "type": "cash",
    "amount": "10000.00",
}

not_enough_money = {
    "type": "cash",
    "amount": "1.00",
}

invalid_payment = {
    "type": "card",
    "amount": "-25.00",
}


@pytest.fixture(scope="module")
def client():
    with TestClient(app=app) as c:
        yield c


def test_login(client):
    response = client.post(
        "/api/v1/signup",
        json={
            "username": "latand",
            "password": "mysecretpassword",
            "full_name": "Latand",
        },
    )
    return response.json()["access_token"]


def test_create_receipt_unauth(client):
    response = client.post(
        "/api/v1/receipts",
        json={"products": [valid_product], "payment": valid_payment},
    )
    assert response.status_code == 401


def test_create_receipt_success(client):
    token = test_login(client)
    response = client.post(
        "/api/v1/receipts",
        json={"products": [valid_product], "payment": valid_payment},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    assert "receipt_id" in response.json()


def test_create_receipt_invalid_product(client):
    token = test_login(client)
    response = client.post(
        "/api/v1/receipts",
        json={"products": [invalid_product], "payment": valid_payment},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422
    assert "detail" in response.json()


def test_create_receipt_invalid_payment(client):
    token = test_login(client)
    response = client.post(
        "/api/v1/receipts",
        json={"products": [valid_product], "payment": invalid_payment},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422
    assert "detail" in response.json()


def test_create_receipt_missing_data(client):
    token = test_login(client)
    response = client.post(
        "/api/v1/receipts", json={}, headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 422
    assert "detail" in response.json()


def test_create_receipt_invalid_data(client):
    token = test_login(client)
    response = client.post(
        "/api/v1/receipts",
        json={"products": [], "payment": {}},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422
    assert "detail" in response.json()


def test_create_receipt_not_enough_money(client):
    token = test_login(client)
    response = client.post(
        "/api/v1/receipts",
        json={"products": [valid_product], "payment": not_enough_money},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400
    assert "detail" in response.json()
    assert "Not enough money" in response.json()["detail"]


def test_multiple_products(client):
    token = test_login(client)
    products = [
        {
            "name": "Product 1",
            "price": "10.50",
            "quantity": "2.5",
            "comment": "Sample comment",
        },
        {
            "name": "Product 2",
            "price": "5.00",
            "quantity": "3",
            "comment": "Another comment",
        },
    ]

    response = client.post(
        "/api/v1/receipts",
        json={"products": products, "payment": valid_payment},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    assert "receipt_id" in response.json()
    assert len(response.json()["products"]) == 2
    assert response.json()["total"] == "41.250"
    assert response.json()["rest"] == "9958.750"
