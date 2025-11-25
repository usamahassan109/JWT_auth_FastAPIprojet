# """
# 1-onlu authentication user fetch the user detail
# 2-A request with invalid token should not be be entertained
# /user/me
# """
# from app.services.user import _generate_tokens


# def test_fetch_me(client,user,test_session):
#     data = _generate_tokens( user,test_session)
#     headers = {
#         "Authorization": f"Beare {data['access_token']}"
#     }
#     response = client.user("/users/me",headers=headers)
#     assert response.status_code == 200
#     assert response.json()["email"] == user.email

# # ------------------------------------------------
# #_____________________________________________________
# def test_fetch_me_invalid_token(client,user,test_session):
#     data = _generate_tokens( user,test_session)
#     headers = {
#         "Authorization": f"Beare {data['access_token'][:-6]}sadk2r" #[:-6]}sadk2r yee cheez hoe ha k last waly token k 6 character change kr do ya minus kr do taa k invalid token ho jay or detail na show ho
#     }
#     response = client.user("/users/me")
#     assert response.status_code == 400
#     assert 'email' in response.json

from app.services.user import _generate_tokens

def test_fetch_me(client, user, test_session):
    # FIXED: correct order session, user
    data = _generate_tokens(test_session, user)

    headers = {
        # FIXED: "Bearer" spelling
        "Authorization": f"Bearer {data['access_token']}"
    }

    # FIXED: client.get() instead of client.user()
    response = client.get("/users/me", headers=headers)

    assert response.status_code == 200
    assert response.json()["email"] == user.email


def test_fetch_me_invalid_token(client, user, test_session):
    # FIXED: correct order
    data = _generate_tokens(test_session, user)

    # corrupt token to make it invalid
    invalid_token = data["access_token"][:-6] + "sadk2r"

    headers = {
        "Authorization": f"Bearer {invalid_token}"
    }

    # FIXED: client.get + headers passed
    response = client.get("/users/me", headers=headers)

    assert response.status_code == 401
    assert 'email' not in response.json()
    assert 'id' not in response.json()
