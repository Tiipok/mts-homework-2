import json
import logging
import os
from functools import partial

import pytest
import requests


REST_BASE_URL = "https://playground.nileslabs.com/api/v1"
GRAPHQL_URL = "https://graphql.postman-echo.com/graphql"
TIMEOUT = 30
logger = logging.getLogger("api")
SECRET_FIELDS = {
    "authorization", "password", "access_token", "refresh_token", "cookie", "set-cookie"
}


def redact(value):
    """Скрываем пароли, токены и cookie в диагностических логах."""
    if isinstance(value, dict):
        return {
            key: "<redacted>" if key.lower() in SECRET_FIELDS else redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value


def as_log_json(value):
    return json.dumps(redact(value), ensure_ascii=False)


@pytest.fixture
def api_request():
    # Новая сессия для каждого теста; внутри сценария сохраняется pg_identity.
    with requests.Session() as session:
        session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json",
        })

        def request(method, path="", *, base_url, **kwargs):
            url = base_url + path
            logger.info(
                "REQUEST %s %s\nHeaders: %s\nJSON: %s",
                method, url,
                as_log_json({**session.headers, **kwargs.get("headers", {})}),
                as_log_json(kwargs.get("json")),
            )
            response = session.request(method, url, timeout=TIMEOUT, **kwargs)
            try:
                body = response.json()
            except ValueError:
                body = response.text
            logger.info(
                "RESPONSE %s %s\nHeaders: %s\nBody: %s",
                response.status_code, response.reason,
                as_log_json(dict(response.headers)), as_log_json(body),
            )
            return response

        yield request


@pytest.fixture
def rest_api(api_request):
    return partial(api_request, base_url=REST_BASE_URL)


@pytest.fixture
def graphql_api(api_request):
    return partial(api_request, "POST", base_url=GRAPHQL_URL)


@pytest.fixture
def credentials():
    # Пароль из актуальной OpenAPI-схемы; отличие от PDF описано в README
    return {
        "username": os.getenv("API_USERNAME", "Bret"),
        "password": os.getenv("API_PASSWORD", "Password@123"),
    }
