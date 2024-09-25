# TESTS

* /_health: Checks that the status code is 200 and the response JSON is {"status": "OK"}.
* /view/{object_id}: Verifies that a GET request to /view/{object_id} results in a 307 redirect and the location header matches the expected URL.
* OpenAPI Endpoint: Tests that the OpenAPI documentation is accessible via /openapi.json.
* Swagger UI: Verifies that the Swagger UI is accessible at /docs and returns an HTML page with the Swagger UI.
* Server Startup: Checks that the FastAPI application starts up successfully using .env or environment variables.
