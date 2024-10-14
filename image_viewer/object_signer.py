from gen3.auth import Gen3Auth
from gen3.file import Gen3File
import logging


def get_signed_url(object_id: str, file_service: Gen3File) -> str:
    """Call Gen3 to get a signed URL for the object_id"""

    file_info = file_service.get_presigned_url(object_id)

    if 'url' not in file_info:
        logging.getLogger("uvicorn.error").error(file_info)

    return file_info['url']
