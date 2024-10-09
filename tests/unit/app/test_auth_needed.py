from urllib.parse import urlparse, parse_qs


def test_view_object_with_bearer_token(client, valid_token):
    object_id = "123"
    headers = {"Authorization": f"Bearer {valid_token}"}
    response = client.get(f"/view/{object_id}", headers=headers, follow_redirects=False)
    assert response.status_code == 307  # Redirect
    assert response.headers["location"].endswith(object_id)


def test_view_object_with_cookie_token(client_with_cookie):
    object_id = "123"
    response = client_with_cookie.get(f"/view/{object_id}", follow_redirects=False)
    assert response.status_code == 307, "should be a redirect"
    parsed_url = urlparse(response.headers["location"])
    query_params = parse_qs(parsed_url.query)
    assert 'image_url' in query_params
    image_url = query_params['image_url'][0]
    assert image_url, f"should end with {object_id}"
    assert ':' not in image_url, "should not contain ':'"
    assert '&' not in image_url, "should not contain '&'"


def test_view_object_without_token(client):
    object_id = "123"
    response = client.get(f"/view/{object_id}", follow_redirects=False)
    assert response.status_code == 404  # Token not found
