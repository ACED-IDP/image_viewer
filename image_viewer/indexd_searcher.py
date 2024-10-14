import urllib

from fastapi import HTTPException
from gen3.auth import Gen3Auth
from gen3.file import Gen3File
from gen3.index import Gen3Index
from image_viewer.object_signer import get_signed_url


def aviator_url(object_id: str, access_token: str, base_url: str) -> str:
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

    auth = Gen3Auth(refresh_file=f"accesstoken:///{access_token}")
    file_service = Gen3File(auth)
    index_service = Gen3Index(auth)

    source_records = index_service.get(object_id)
    if not isinstance(source_records, list) or len(source_records) != 1:
        raise HTTPException(status_code=500, detail=f"Could not find object with id {object_id} {source_records}")
    source_record = source_records[0]
    if "file_name" not in source_record:
        raise HTTPException(status_code=500, detail=f"Could not find file_name within {source_record}")
    if "ome.tif" not in source_record["file_name"]:
        raise HTTPException(status_code=500, detail=f"Expected file_name to contain 'ome.tif' {source_record}")
    source_file_name = source_record["file_name"]

    offset_file_name = source_file_name.replace("ome.tif", "offsets.json")
    offsets_records = index_service.query_urls(offset_file_name, {"include": offset_file_name})
    if not isinstance(offsets_records, list) or len(offsets_records) != 1:
        raise HTTPException(status_code=500,
                            detail=f"Could not find object with file_name {offset_file_name} {offsets_records}")
    offsets_record = offsets_records[0]
    if "did" not in offsets_record:
        raise HTTPException(status_code=500, detail=f"Could not find did within {offsets_record}")
    offsets_object_id = offsets_record["did"]

    # get the signed url for the source object
    source_signed_url = get_signed_url(object_id, file_service)
    offsets_signed_url = get_signed_url(offsets_object_id, file_service)

    # Use the configurable base_url from settings
    # we encode the signed url because it will contain special characters
    redirect_url = f"{base_url}{urllib.parse.quote_plus(source_signed_url)}{urllib.parse.quote_plus(f'&offsets_url={offsets_signed_url}')}"
    return redirect_url
