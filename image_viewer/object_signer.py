import logging
import urllib.parse
from typing import Optional

import requests
from fastapi import HTTPException


logger = logging.getLogger(__name__)


def get_object(object_id: str, access_token: str, syfon_url: str) -> dict:
    """Fetch a DRS object from Syfon."""
    return _get_json(f"{_base_url(syfon_url)}/objects/{_quote_path(object_id)}", access_token)


def query_url(object_url: str, access_token: str, syfon_url: str) -> list:
    """Return Syfon/index-compatible records that reference object_url."""
    payload = _get_json(
        f"{_base_url(syfon_url)}/index",
        access_token,
        params={"url": object_url, "limit": 1},
    )
    records = payload.get("records", [])
    if not isinstance(records, list):
        raise HTTPException(status_code=500, detail=f"Unexpected Syfon /index response: {payload}")
    return records


def get_signed_url(object_id: str, access_token: str, syfon_url: str, drs_object: Optional[dict] = None) -> str:
    """Ask Syfon for a signed URL for the object's first access method."""
    drs_object = drs_object or get_object(object_id, access_token, syfon_url)
    access_methods = drs_object.get("access_methods", [])
    if not isinstance(access_methods, list) or len(access_methods) == 0:
        raise HTTPException(status_code=500, detail=f"Object has no access methods: {object_id}")

    access_method = access_methods[0]
    access_id = access_method.get("access_id") or access_method.get("type")
    if not access_id:
        raise HTTPException(status_code=500, detail=f"Object access method has no access_id: {object_id}")

    signed = _get_json(
        f"{_base_url(syfon_url)}/objects/{_quote_path(object_id)}/access/{_quote_path(access_id)}",
        access_token,
    )
    if "url" not in signed:
        logger.error("Syfon access response missing url: %s", signed)
        raise HTTPException(status_code=500, detail=f"Syfon access response missing url: {object_id}")
    return signed["url"]


def _get_json(url: str, access_token: str, **kwargs) -> dict:
    try:
        response = requests.get(url, headers={"Authorization": f"Bearer {access_token}"}, timeout=30, **kwargs)
    except requests.RequestException as err:
        raise HTTPException(status_code=502, detail=f"Syfon request failed: {err}") from err
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    try:
        return response.json()
    except ValueError as err:
        raise HTTPException(status_code=502, detail=f"Syfon returned non-JSON response from {url}") from err


def _base_url(syfon_url: str) -> str:
    base = syfon_url.strip().rstrip("/")
    if not base:
        raise HTTPException(status_code=500, detail="SYFON_URL is not configured")
    return base


def _quote_path(value: str) -> str:
    return urllib.parse.quote(value, safe="")
