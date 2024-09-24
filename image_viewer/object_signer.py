from gen3.auth import Gen3Auth
from gen3.file import Gen3File


def get_signed_url(object_id: str, access_token: str) -> str:
    """Call Gen3 to get a signed URL for the object_id"""
    auth = Gen3Auth(access_token=access_token)
    file = Gen3File(auth)
    return file.get_presigned_url(object_id)['url']
