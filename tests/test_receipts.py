from decimal import Decimal
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
}

invalid_product = {
    "name": "Product 2",
    "price": "10.50",
    "quantity": "-2.5",
}

valid_payment_cash = {
    "type": "cash",
    "amount": "10000.00",
}
valid_payment_card = {
    "type": "card",
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
        json={"products": [valid_product], "payment": valid_payment_cash},
    )
    assert response.status_code == 401


def test_create_receipt_success(client):
    token = test_login(client)
    response = client.post(
        "/api/v1/receipts",
        json={"products": [valid_product], "payment": valid_payment_cash},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    assert "receipt_id" in response.json()


def test_create_receipt_invalid_product(client):
    token = test_login(client)
    response = client.post(
        "/api/v1/receipts",
        json={"products": [invalid_product], "payment": valid_payment_cash},
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
        },
        {
            "name": "Product 2",
            "price": "5.00",
            "quantity": "3",
        },
    ]

    response = client.post(
        "/api/v1/receipts",
        json={
            "products": products,
            "payment": valid_payment_cash,
            "comment": "Testing",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    assert "receipt_id" in response.json()
    assert len(response.json()["products"]) == 2
    assert response.json()["total"] == "41.250"
    assert response.json()["rest"] == "9958.750"
    assert response.json()["comment"] == "Testing"


def test_many_products_large_names(client):
    token = test_login(client)
    products = [
        {
            "name": "Product 1",
            "price": "10.50",
            "quantity": "2.5",
        },
        {
            "name": "Product 2 " * 2,
            "price": "5.00",
            "quantity": "3",
        },
        {
            "name": "Product 3 " * 3,
            "price": "7.00",
            "quantity": "10",
        },
        {
            "name": "Product 4" * 4,
            "price": "3.50",
            "quantity": "5",
        },
    ]

    response = client.post(
        "/api/v1/receipts",
        json={"products": products, "payment": valid_payment_card, "comment": "Test"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    assert "receipt_id" in response.json()
    assert len(response.json()["products"]) == 4
    assert response.json()["comment"] == "Test"


def test_get_receipts(client):
    token = test_login(client)
    response = client.get(
        "/api/v1/receipts", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    receipts = response.json()
    assert isinstance(response.json(), list)
    assert len(receipts) > 0


def test_get_receipts_by_date(client):
    token = test_login(client)
    response = client.get(
        "/api/v1/receipts?start_date=2024-05-01&end_date=2024-06-01",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    receipts = response.json()
    assert len(receipts) > 0
    assert all("2024-05-01" in receipt["created_at"] for receipt in receipts)


def test_get_receipts_by_min_total(client):
    token = test_login(client)
    response = client.get(
        "/api/v1/receipts?min_total=40", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    receipts = response.json()
    assert len(receipts) > 0
    assert all(Decimal(receipt["total"]) >= 40 for receipt in receipts)


def test_get_receipts_by_max_total(client):
    token = test_login(client)
    response = client.get(
        "/api/v1/receipts?max_total=30", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    receipts = response.json()
    assert len(receipts) > 0
    assert all(Decimal(receipt["total"]) <= 30 for receipt in receipts)


def test_get_receipts_by_payment_type_cash(client):
    token = test_login(client)
    response = client.get(
        "/api/v1/receipts?payment_type=cash",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    receipts = response.json()
    assert len(receipts) > 0
    assert all(receipt["payment"]["type"] == "cash" for receipt in receipts)


def test_get_receipts_by_payment_type_card(client):
    token = test_login(client)
    response = client.get(
        "/api/v1/receipts?payment_type=card",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    receipts = response.json()
    assert len(receipts) > 0
    assert all(receipt["payment"]["type"] == "card" for receipt in receipts)


def test_pagination(client):
    token = test_login(client)
    response = client.get(
        "/api/v1/receipts?limit=2&offset=1",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    receipts = response.json()
    assert len(receipts) <= 2


def test_get_receipts_no_filters(client):
    token = test_login(client)
    response = client.get(
        "/api/v1/receipts", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    receipts = response.json()
    assert len(receipts) > 0


def test_get_receipt_by_id(client):
    response = client.get("/api/v1/receipts/3")
    assert response.status_code == 200
    assert "receipt_id" in response.json()


def test_show_receipt_length(client):
    lengths = [20, 30, 40, 50]
    for length in lengths:
        response = client.get(f"/api/v1/receipts/show/3?max_characters={length}")
        assert response.status_code == 200
        response_text = response.text

        for line in response_text.split("\n"):
            assert len(line) <= length
