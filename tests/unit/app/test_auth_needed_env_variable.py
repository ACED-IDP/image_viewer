import os

import pytest
from fastapi.testclient import TestClient
import image_viewer.app
from tests.unit.app.conftest import monkey_patch_gen3_signed_url


@pytest.fixture
def client_with_cookie_base_url(monkeypatch, base_url, valid_token):
    # Set the environment variable using monkeypatch
    os.environ["BASE_URL"] = base_url
    assert os.getenv("BASE_URL") == base_url

    monkey_patch_gen3_signed_url(monkeypatch)
    client_ = TestClient(image_viewer.app.app)

    client_.cookies.update({"access_token": valid_token})
    yield client_


# Test setting base_url via environment variable
def test_base_url_from_env_variable(monkeypatch, client_with_cookie_base_url, base_url):

    object_id = "123"
    response = client_with_cookie_base_url.get(f"/view/{object_id}", follow_redirects=False)

    # Assert that the base_url comes from the environment variable
    assert response.status_code == 307
    assert response.headers["location"].endswith(object_id)
