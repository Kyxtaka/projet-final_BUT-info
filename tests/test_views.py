import os
import tempfile
from flask import Flask
from flask_sqlalchemy  import SQLAlchemy
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
import datetime
from flask import session
import pytest
from mobilist.app import mkpath, app, db

# racine projet (pas mobilist) python -m pytest
@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        yield client

def test_about_page(client):
    response = client.get("/about")
    assert response.status_code == 404
    response = client.get("/information")
    assert response.status_code == 200

def test_accueil_page(client):
    response = client.get("/accueil")
    assert response.status_code == 200

def test_services(client):
    response = client.get("/services")
    assert response.status_code == 200

def test_avis(client):
    response = client.get("/avis")
    assert response.status_code == 200
    assert b'NATHAN' in response.data

def test_login(client):
    response = client.get("/login")
    assert response.status_code == 308

def test_login_success(client):
    response = client.post(
        "/login/",
        data={"username": "clemence.bcq@gmail.com", "password": "1234"},
        follow_redirects=True, 
    )
    assert response.status_code == 200  


    
