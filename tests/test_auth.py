from uuid import uuid4

import pytest


def test_login_token_grants_access_to_current_user(rest_api, credentials):
    response = rest_api("POST", "/auth/login", json=credentials)
    assert response.status_code == 200
    login = response.json()
    token = login["access_token"]
    assert isinstance(token, str) and token.strip()
    logged_in_user = login["user"]
    assert logged_in_user["username"].casefold() == credentials["username"].casefold()

    response = rest_api("GET", "/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    profile = response.json()
    assert isinstance(profile["id"], int) and profile["id"] > 0
    for field in ("id", "username", "name", "email"):
        assert profile[field]
        assert profile[field] == logged_in_user[field]


@pytest.mark.parametrize(
    "authorization",
    [None, "Bearer definitely-invalid-token"],
    ids=["missing-token", "invalid-token"],
)
def test_current_user_rejects_unauthorized_request(rest_api, authorization):
    headers = {} if authorization is None else {"Authorization": authorization}
    response = rest_api("GET", "/auth/me", headers=headers)
    assert response.status_code == 401
    error = response.json()
    assert error["status"] == 401
    assert "unauthorized" in error["error"].casefold()
    assert error["message"] == error["error"]
    assert "id" not in error


@pytest.mark.parametrize("invalid_field", ["username", "password"])
def test_login_rejects_invalid_credentials(rest_api, credentials, invalid_field):
    """Дополнительный сценарий: неизвестный логин или неправильный пароль."""
    invalid_credentials = {
        **credentials,
        invalid_field: f"does-not-exist-{uuid4().hex}",
    }
    response = rest_api("POST", "/auth/login", json=invalid_credentials)
    assert response.status_code == 401
    error = response.json()
    assert error["status"] == 401
    assert error["error"] == "Invalid username or password."
    assert error["message"] == error["error"]
    assert "access_token" not in error
    assert "refresh_token" not in error
