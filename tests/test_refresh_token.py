from app.services.user import _generate_tokens
import logging
def test_refresh_token(client, user, test_session):
    data = _generate_tokens(test_session, user)
    headers = {"refresh-token": data['refresh_token']}

    response = client.post("/auth/refresh",json={}, headers=headers)  # ✅ correct URL
    assert response.status_code == 200
    json_data = response.json()
    assert 'access_token' in json_data
    assert 'refresh_token' in json_data



def test_refresh_token_with_invalid_token(client, user, test_session):
    data = _generate_tokens(test_session, user)  # ✅ fixed order
    headers = {
        "refresh-token": 'hgsysdagfa8ingkasasgfasfjf'
    }
    response = client.post("/auth/refresh",json={}, headers=headers)
    assert response.status_code == 404
    assert 'access_token' not in response.json()
    assert 'refresh_token' not in response.json()