from urllib.parse import unquote

import requests

from image_viewer.indexd_searcher import aviator_url
from image_viewer.object_signer import get_signed_url, query_url


class FakeResponse:
    def __init__(self, payload, status_code=200, text=""):
        self._payload = payload
        self.status_code = status_code
        self.text = text

    def json(self):
        return self._payload


def test_query_url_uses_syfon_index_url_filter(monkeypatch):
    calls = []

    def fake_get(url, **kwargs):
        calls.append((url, kwargs))
        return FakeResponse({"records": [{"did": "offsets-id"}]})

    monkeypatch.setattr(requests, "get", fake_get)

    records = query_url("s3://bucket/image.offsets.json", "token", "https://syfon.example")

    assert records == [{"did": "offsets-id"}]
    assert calls[0][0] == "https://syfon.example/index"
    assert calls[0][1]["params"] == {"url": "s3://bucket/image.offsets.json", "limit": 1}
    assert calls[0][1]["headers"] == {"Authorization": "Bearer token"}


def test_get_signed_url_uses_drs_access_endpoint(monkeypatch):
    calls = []

    def fake_get(url, **kwargs):
        calls.append((url, kwargs))
        return FakeResponse({"url": "https://signed.example/object"})

    monkeypatch.setattr(requests, "get", fake_get)

    signed = get_signed_url(
        "object/id",
        "token",
        "https://syfon.example/",
        {"access_methods": [{"access_id": "s3/main", "access_url": {"url": "s3://bucket/image.ome.tif"}}]},
    )

    assert signed == "https://signed.example/object"
    assert calls[0][0] == "https://syfon.example/ga4gh/drs/v1/objects/object%2Fid/access/s3%2Fmain"


def test_aviator_url_resolves_offsets_through_syfon(monkeypatch):
    calls = []

    def fake_get(url, **kwargs):
        calls.append((url, kwargs))
        if url.endswith("/ga4gh/drs/v1/objects/source-id"):
            return FakeResponse(
                {
                    "id": "source-id",
                    "access_methods": [
                        {"access_id": "source-access", "access_url": {"url": "s3://bucket/image.ome.tif"}},
                    ],
                }
            )
        if url.endswith("/index"):
            assert kwargs["params"] == {"url": "s3://bucket/image.offsets.json", "limit": 1}
            return FakeResponse({"records": [{"did": "offsets-id"}]})
        if url.endswith("/ga4gh/drs/v1/objects/source-id/access/source-access"):
            return FakeResponse({"url": "https://signed.example/source?x=1"})
        if url.endswith("/ga4gh/drs/v1/objects/offsets-id"):
            return FakeResponse(
                {
                    "id": "offsets-id",
                    "access_methods": [
                        {"access_id": "offsets-access", "access_url": {"url": "s3://bucket/image.offsets.json"}},
                    ],
                }
            )
        if url.endswith("/ga4gh/drs/v1/objects/offsets-id/access/offsets-access"):
            return FakeResponse({"url": "https://signed.example/offsets?x=2"})
        raise AssertionError(f"unexpected Syfon request: {url}")

    monkeypatch.setattr(requests, "get", fake_get)

    redirect = aviator_url("source-id", "token", "/aviator/?image_url=", "https://syfon.example")

    assert redirect.startswith("/aviator/?image_url=")
    assert "offsets_url=" in redirect
    assert unquote(redirect).count("https://signed.example/source?x=1") == 1
    assert unquote(redirect).count("https://signed.example/offsets?x=2") == 1
    assert [call[0] for call in calls] == [
        "https://syfon.example/ga4gh/drs/v1/objects/source-id",
        "https://syfon.example/index",
        "https://syfon.example/ga4gh/drs/v1/objects/source-id/access/source-access",
        "https://syfon.example/ga4gh/drs/v1/objects/offsets-id",
        "https://syfon.example/ga4gh/drs/v1/objects/offsets-id/access/offsets-access",
    ]
