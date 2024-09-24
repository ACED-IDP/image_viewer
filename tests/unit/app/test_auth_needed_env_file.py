import os.path

import pytest
from fastapi.testclient import TestClient
import image_viewer.app

from tests.unit.app.conftest import monkey_patch_gen3_signed_url


@pytest.fixture(scope="function")
def client_with_cookie_env_file(monkeypatch, valid_token):
    # Set the environment variable using monkeypatch
    current_dir = os.path.curdir
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    monkey_patch_gen3_signed_url(monkeypatch)
    client_ = TestClient(image_viewer.app.app)
    client_.cookies.update({"access_token": valid_token})
    yield client_
    os.chdir(current_dir)


# Test loading config from .env file
def test_base_url_from_env_file(monkeypatch, client_with_cookie_env_file):

    # Test the default behavior (without overriding environment variables)
    object_id = "123"
    response = client_with_cookie_env_file.get(f"/view/{object_id}", follow_redirects=False)

    # Assert that the base_url comes from the .env file
    expected_base_url = 'https://env-file-url.com/objects/'
    assert response.status_code == 307
    assert response.headers["location"].startswith(expected_base_url)
    assert response.headers["location"].endswith(object_id)
