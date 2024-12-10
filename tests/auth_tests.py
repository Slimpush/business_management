from fastapi.testclient import TestClient
import pytest


def test_sign_up(api_client_without_auth: TestClient):
    sign_up_data = {
        "account": "test_user@example.com",
        "token": "valid-invite-token",
        "first_name": "Test",
        "last_name": "User",
        "password": "securepassword123"
    }

    response = api_client_without_auth.post("/api/v1/sign-up/", json=sign_up_data)

    assert response.status_code == 200
    assert response.json()["message"] == "Account successfully verified."
    assert response.json()["account"] == sign_up_data["account"]


def test_sign_in(api_client_without_auth: TestClient):
    sign_up_data = {
        "account": "test_user@example.com",
        "token": "valid-invite-token",
        "first_name": "Test",
        "last_name": "User",
        "password": "securepassword123"
    }
    api_client_without_auth.post("/api/v1/sign-up/", json=sign_up_data)

    sign_in_data = {
        "account": "test_user@example.com",
        "password": "securepassword123"
    }

    response = api_client_without_auth.post("/api/v1/sign-in", json=sign_in_data)

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "Bearer"
    assert response.json()["access_token"] == "fake-jwt-token"


@pytest.mark.parametrize(
    "sign_up_data, expected_status, expected_detail",
    [
        (
            {"account": "test_user@example.com", "token": "invalid-token", "first_name": "Test", "last_name": "User", "password": "securepassword123"},
            400,
            "Invalid or missing verification code."
        ),
    ]
)
def test_sign_up_exceptions_without_auth(api_client_without_auth: TestClient, sign_up_data, expected_status, expected_detail):
    response = api_client_without_auth.post("/api/v1/sign-up/", json=sign_up_data)

    assert response.status_code == expected_status
    assert expected_detail in response.json()["detail"]
