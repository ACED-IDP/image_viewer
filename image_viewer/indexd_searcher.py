import urllib

from fastapi import HTTPException
from image_viewer.object_signer import get_object, get_signed_url, query_url
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def aviator_url(object_id: str, access_token: str, base_url: str, syfon_url: str) -> str:
    """Return the URL for the Aviator image viewer.
    object_id: str The object ID of an ome.tif file to view
    access_token: str The access token to use for authentication
    base_url: str The base URL for the Aviator image viewer

    Returns: str The URL for the Aviator image viewer

    Raises: HTTPException if the object cannot be found or the file name is incorrect

    Validate the object_id and access_token, then get the signed URL for the object and its offsets.json file.
    Offset file is looked up by replacing "ome.tif" with "offsets.json" in the file_name. See https://github.com/hms-dbmi/viv/blob/main/sites/avivator/src/utils.js#L151-L159
    Construct the URL for the Aviator image viewer using the signed URLs.
    """

    source_record = get_object(object_id, access_token, syfon_url)
    if not isinstance(source_record, dict):
        raise HTTPException(status_code=500, detail=f"Could not find object with id {object_id} {source_record}")
    logger.error(f"aviator_url source_record {source_record}")
    access_methods = source_record.get("access_methods", [])
    if not isinstance(access_methods, list) or len(access_methods) == 0:
        raise HTTPException(status_code=500, detail=f"Could not find access methods within {source_record}")

    source_access_url = access_methods[0].get("access_url") or {}
    source_url = source_access_url.get("url")
    if not source_url:
        raise HTTPException(status_code=500, detail=f"Could not find source URL within {source_record}")
    if "ome.tif" not in source_url:
        raise HTTPException(status_code=500, detail=f"Expected url to contain 'ome.tif' {source_record}")

    offset_file_url = source_url.replace("ome.tiff", "offsets.json").replace("ome.tif", "offsets.json")
    offsets_records = query_url(offset_file_url, access_token, syfon_url)
    if not isinstance(offsets_records, list) or len(offsets_records) == 0:
        raise HTTPException(status_code=500,
                            detail=f"Could not find object with url {offset_file_url} {offsets_records}")
    offsets_record = offsets_records[0]
    if "did" not in offsets_record and "id" not in offsets_record:
        raise HTTPException(status_code=500, detail=f"Could not find did within {offsets_record}")
    offsets_object_id = offsets_record.get("did") or offsets_record["id"]

    # get the signed url for the source object
    source_signed_url = get_signed_url(object_id, access_token, syfon_url, source_record)
    offsets_signed_url = get_signed_url(offsets_object_id, access_token, syfon_url)

    # Use the configurable base_url from settings
    # we encode the signed url because it will contain special characters
    redirect_url = f"{base_url}{urllib.parse.quote_plus(source_signed_url)}&offsets_url={urllib.parse.quote_plus(offsets_signed_url)}"
    return redirect_url
