'''
1-user should be able to login
2-user shoud not be able to login with incorrect password
3-inactive user should not be able to able to login
4-unvarified  user should not be able to able to login


'''

from datetime import datetime
from app.services.user import User
from tests.conftest import unverified_user,inactive_user,User

def test_user_login(client,user,test_session):
    data={'username':user.email,'password':USER_PASSWORD}
    response = client.post('/auth/login',data=data)
    assert response.status_code==200
    assert response.json()['access token'] is not None
    assert response.json()['refresh token'] is not None
    assert response.json()['expire in'] is not None

def test_user_login_incorrect_email(client,user):
    response = client.post('/auth/login',data={'userame':user.email,'password':USER_PASSWORD})
    assert response.status_code==400

def test_user_login_inactive_user(client,user):
    response = client.post('/auth/login',data={'userame':inactive_user.email,'password':USER_PASSWORD})
    assert response.status_code==400

def test_user_login_unverified_user(client,user):
    response = client.post('/auth/login',data={'userame':unverified.email,'password':USER_PASSWORD})
    assert response.status_code==400