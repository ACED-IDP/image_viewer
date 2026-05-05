import urllib.parse
from importlib import reload

from fastapi.testclient import TestClient
import pytest
import image_viewer.app


@pytest.fixture
def client(monkeypatch):
    monkey_patch_mocks(monkeypatch)
    reload(image_viewer.app)  # reload the app to pick up the new environment variable
    yield TestClient(image_viewer.app.app)


@pytest.fixture
def client_with_cookie(valid_token, monkeypatch):
    monkey_patch_mocks(monkeypatch)
    client_ = TestClient(image_viewer.app.app)
    client_.cookies.update({"access_token": valid_token})
    yield client_


@pytest.fixture
def base_url():
    return "https://custom-env-url.com/objects/"


@pytest.fixture
def valid_token():
    """John Doe token"""
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJpc3MiOiJodHRwOi8vZXhhbXBsZS5jb20ifQ.r9Ub3dCTuPxQvPkb1aT7pMaw-H7udMHYMfFlY1II3qA"


def monkey_patch_mocks(monkeypatch):
    """Monkey patch for testing."""
    monkey_patch_aviator(monkeypatch)


def monkey_patch_aviator(monkeypatch):
    """Monkey patch the Aviator URL response."""
    import image_viewer.indexd_searcher

    def mock_aviator_url(object_id, access_token, base_url, syfon_url):
        """Mock the Aviator URL response"""
        image_url = urllib.parse.quote_plus(f'https://image-{object_id}')
        offsets_url = urllib.parse.quote_plus(f'https://offsets-{object_id}')
        parms = f'image_url={image_url}&offsets_url={offsets_url}'
        _ = f"https://env-file-url.com/objects/?{parms}"
        print(f"Mocked aviator_url: {object_id} {access_token} {base_url} {syfon_url} -> {_}")
        return _

    monkeypatch.setattr(image_viewer.indexd_searcher, "aviator_url", mock_aviator_url)
    print("Monkey patched aviator_url")

