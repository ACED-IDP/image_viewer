import hashlib
import urllib

from fastapi import HTTPException, Request
from gen3.auth import Gen3Auth
from gen3.file import Gen3File
from gen3.index import Gen3Index

from image_viewer import cache
from image_viewer.object_signer import get_signed_url
import logging
import re
from dataclasses import dataclass

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@dataclass
class RegexEqual(str):
    string: str
    match: re.Match = None

    def __eq__(self, pattern):
        self.match = re.search(pattern, self.string)
        return self.match is not None


def aviator_url(source_record, base_url, file_service, index_service):
    """Return the URL for the Aviator image viewer."""
    source_file_name = source_record["file_name"]

    offset_file_name = source_file_name.replace("ome.tiff", "offsets.json")
    offset_file_name = offset_file_name.replace("ome.tif", "offsets.json")
    offsets_records = index_service.query_urls(offset_file_name)
    if not isinstance(offsets_records, list) or len(offsets_records) != 1:
        raise HTTPException(status_code=404,
                            detail=f"Could not find object with file_name {offset_file_name} {offsets_records}")
    offsets_record = offsets_records[0]
    if "did" not in offsets_record:
        raise HTTPException(status_code=404, detail=f"Could not find did within {offsets_record}")
    offsets_object_id = offsets_record["did"]

    # get the signed url for the source object
    object_id = source_record["did"]
    source_signed_url = get_signed_url(object_id, file_service)
    offsets_signed_url = get_signed_url(offsets_object_id, file_service)

    # Use the configurable base_url from settings
    # we encode the signed url because it will contain special characters
    redirect_url = f"{base_url}{urllib.parse.quote_plus(source_signed_url)}&offsets_url={urllib.parse.quote_plus(offsets_signed_url)}"
    return redirect_url


def genome_browser_url(source_record, base_url, access_token, file_service, index_service):
    """Return the URL for the genome browser."""
    vcf_file_name = source_record["file_name"]

    tbi_file_name = vcf_file_name + ".tbi"
    tbi_records = index_service.query_urls(tbi_file_name)
    if not isinstance(tbi_records, list) or len(tbi_records) != 1:
        raise HTTPException(status_code=404,
                            detail=f"Could not find object with file_name {tbi_file_name} {tbi_records}")
    tbi_record = tbi_records[0]
    if "did" not in tbi_record:
        raise HTTPException(status_code=404, detail=f"Could not find did within {tbi_record}")
    tbi_object_id = tbi_record["did"]

    # get the signed url for the source object
    object_id = source_record["did"]
    source_signed_url = get_signed_url(object_id, file_service)
    tbi_signed_url = get_signed_url(tbi_object_id, file_service)

    # Use the configurable base_url from settings
    # we encode the signed url because it will contain special characters
    access_token_hash = hashlib.md5(access_token.encode()).hexdigest()
    cache.set(f"{object_id}_{access_token_hash}", {
        "source": source_signed_url,
        "tbi": tbi_signed_url
    })
    # coordinate
    hub_url = f"{base_url}/ucsc/{access_token_hash}/{object_id}"
    redirect_url = f"http://genome.ucsc.edu/cgi-bin/hgTracks?hubUrl={urllib.parse.quote_plus(hub_url)}"
    return redirect_url


def redirection_url(object_id: str, access_token: str, base_url: str, request: Request) -> str:
    """Return the URL for the object.
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

    logger.error(f"in redirection_url")

    source_record = index_service.get(object_id)
    if not isinstance(source_record, dict):
        raise HTTPException(status_code=404, detail=f"Could not find object with id {object_id} {source_record}")

    logger.error(f"redirection_url source_record {source_record}")

    if "file_name" not in source_record:
        raise HTTPException(status_code=500, detail=f"Could not find file_name within {source_record}")

    redirect_url = None
    match RegexEqual(source_record['file_name']):
        case "\\.ome.tif?":
            redirect_url = aviator_url(source_record, base_url, file_service, index_service)
        case "\\.vcf":
            redirect_url = genome_browser_url(source_record, request.base_url, access_token, file_service, index_service)

    if not redirect_url:
        raise HTTPException(status_code=500, detail=f"Could not match a viewer for {source_record['file_name']}")

    return redirect_url
