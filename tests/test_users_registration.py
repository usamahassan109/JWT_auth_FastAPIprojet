#test create method here we create tests meansgs here we create users
from tests.conftest import USER_NAME,USER_EMAIL,USER_PASSWORD

def test_create_user(client):  #client is import from test folder conftest.py client 
    data={
        "name":USER_NAME,
        "email":USER_EMAIL,
        "password":USER_PASSWORD
    }
    response = client.post('/users',json=data)
    assert response.status_code == 201
   
def test_create_user_with_existing_email(client, inactive_user):
    """

    🚫 Test: Try creating user with an existing email
    Should not return 201 Created
    """
    data = {
        "name": "Keshari Nandan",
        "email": inactive_user.email,  # same email as before
        "password": USER_PASSWORD
    }

    response = client.post("/users", json=data)
    assert response.status_code != 201  # should fail if duplicate

def test_create_user_with_invalid_email(client):
    data = {
    "name": "Keshari Nandan",
    "email": "keshari.com",
    "password": USER_PASSWORD
    }
    response = client.post("/users/", json=data)
    assert response.status_code != 201

def test_create_user_with_empty_password(client):
    data = {
    "name": "Keshari Nandan",
    "email": USER_EMAIL,
    "password": ""
    }
    response = client.post("/users/", json=data)
    assert response.status_code != 201

def test_create_user_with_numeric_password(client): 
    """🚫 Test numeric-only password""" 
    data = { 
        "name": "Keshari Nandan", 
        "email": USER_EMAIL, 
        "password": "1232382318763" } 
    response = client.post("/users", json=data) 
    assert response.status_code != 201