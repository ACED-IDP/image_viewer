import os
import urllib.parse

import requests
from fastapi import FastAPI, HTTPException, Header, Cookie
from fastapi.responses import RedirectResponse
import uvicorn
import threading

from gen3.auth import Gen3Auth
from gen3.file import Gen3File
from gen3.index import Gen3Index
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from image_viewer.indexd_searcher import aviator_url
from image_viewer.object_signer import get_signed_url

AVIVATOR_URL = "https://avivator.gehlenborglab.org/?image_url="
VITESSCE_URL = "https://vitessce.io/?url=data:,{API OUTPUT HERE}"  # TODO: Add the view config API here, including the signed url See https://python-docs.vitessce.io/api_config.html#vitessce.config.VitessceConfig.add_dataset


# Configuration class using pydantic BaseSettings
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    base_url: str = Field(default=os.getenv("BASE_URL", AVIVATOR_URL))


# Load configuration
settings = Settings()

# load our app
app = FastAPI(settings=settings)


@app.get("/_health", summary="Health Check", description="Indicates server is running, returns a 200 OK status.")
async def health_check():
    return {"status": "OK"}


@app.get("/view/{object_id}",
         summary="View Object",
         description="Redirects to a URL for the object.",
         responses={307: {"description": "Temporary Redirect"}})
async def view_object(object_id: str, authorization: str = Header(None), access_token: str = Cookie(None)):

    token = None

    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]  # Extract token from "Bearer <token>"
    elif access_token:
        token = access_token

    # If no token is found, raise a 404 Not Found error
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")

    try:
        redirect_url = aviator_url(object_id, token, settings.base_url)
        return RedirectResponse(url=redirect_url)
    except requests.exceptions.HTTPError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))


# Make the application multi-threaded
def run_server():
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=4)  # workers=4 makes the app multi-threaded.


if __name__ == "__main__":
    # Running the server in a separate thread.
    server_thread = threading.Thread(target=run_server)
    server_thread.start()
