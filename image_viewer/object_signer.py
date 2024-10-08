from gen3.auth import Gen3Auth
from gen3.file import Gen3File
import logging


def get_signed_url(object_id: str, access_token: str) -> str:
    """Call Gen3 to get a signed URL for the object_id"""

    logger = logging.getLogger("uvicorn.error")

    auth = Gen3Auth(refresh_file=f"accesstoken:///{access_token}")

    file = Gen3File(auth)
    file_info = file.get_presigned_url(object_id)

    if 'url' not in file_info:
        logger.error(file_info)

    return file_info['url']
