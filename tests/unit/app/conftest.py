import urllib.parse
from importlib import reload
from fastapi import Request
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

    def mock_aviator_url(object_id, access_token, base_url, request: Request):
        """Mock the Aviator URL response"""
        print("In mock_aviator_url")
        image_url = urllib.parse.quote_plus(f'https://image-{object_id}')
        offsets_url = urllib.parse.quote_plus(f'https://offsets-{object_id}')
        parms = f'image_url={image_url}&offsets_url={offsets_url}'
        _ = f"https://env-file-url.com/objects/?{parms}"
        print(f"Mocked redirection_url: {object_id} {access_token} {base_url} -> {_}")
        return _

    monkeypatch.setattr(image_viewer.indexd_searcher, "redirection_url", mock_aviator_url)
    print("Monkey patched redirection_url")
    # print(image_viewer.indexd_searcher.redirection_url("123", "456", "789", None))


def monkey_patch_signed_url(monkeypatch):
    """Monkey patch the Gen3 signed URL response.  NOTE: NOT USED CURRENTLY."""
    # TODO - deprecate this function if we are not going to use it.
    import requests  # noqa
    reload(image_viewer.app)  # reload the app to pick up the new environment variable

    def mock_signed_url(api_url, auth):
        """Mock the signed URL response"""
        response_ = requests.Response()
        response_.status_code = 200
        assert 'user/data/download/' in api_url
        object_id_ = api_url.split('/')[-1]
        url = urllib.parse.quote("https://example.com/signed-url-for-object/?foo=bar&id=" + object_id_)
        response_.json = lambda: {"url": url}
        return response_

    monkeypatch.setattr(requests, "get", mock_signed_url)
    print("Monkey patched requests.get")
