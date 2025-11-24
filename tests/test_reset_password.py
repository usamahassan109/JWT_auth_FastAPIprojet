"""
1-user should be able to reset the password by using combination of valid token and valid email
2-user should not reset the password with invalid token
3-user should not reset the password with invalid email
4-user should not reset the password with any email and any token
"""
from app.config.security import hash_password
from app.utils.forgot_password import FORGOT_PASSWORD

NEW_PASSWORD = "#Usama456"

def _get_token(user):
    string_context = user.get_context_string(context=FORGOT_PASSWORD)
    return hash_password(string_context)

  
def test_reset_password(client,user):
    data = {
        "token": _get_token(user),
        "email": user.email,
        "password" : NEW_PASSWORD
    }
    response = client.put("/auth/reset_password", json=data)
    assert response.status_code == 200
    del data['token']
    del data['email']
    data['username'] = user.email
    login_resp = client.post("/auth/login",data= data)
    assert login_resp.status_code == 200

    
def test_reset_password_invalid_token(client,user):
    data = {
        "token": "abshashsdschsdfoshsfhudsj",
        "email": user.email,
        "password" : NEW_PASSWORD
    }
    response = client.put("/auth/reset_password", json = data)
    assert response.status_code == 400
    login_resp = client.post("/auth/login",data= data)
    assert login_resp.status_code != 200

def test_reset_password_invalid_email(client,user):
    data = {
        "token": _get_token(user),
        "email": "uxama11122.com",
        "password" : NEW_PASSWORD
    }
    response = client.put("/auth/reset_password", json = data)
    assert response.status_code == 422

    del data["token"]
    del data["email"]
    data["username"] = user.email
    login_resp = client.post("/auth/login",data= data)
    assert login_resp.status_code != 200

def test_reset_password_different_email(client,user):
    data = {
        "token": _get_token(user),
        "email": "usamahassan7676@gmail.com",
        "password" : NEW_PASSWORD
    }
    response = client.put("/auth/reset_password", json = data)
    assert response.status_code == 400

    del data["token"]
    del data["email"]
    data["username"] = user.email
    login_resp = client.post("/auth/login",data= data)
    assert login_resp.status_code != 200

