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
from unittest.mock import patch
from mobilist.models.classes.User import User  
from mobilist.models.classes.Proprietaire import Proprietaire  

from flask_login import login_user

# racine projet (pas mobilist) python -m pytest
@pytest.fixture
def client():
    """ Set le contexte des tests Flask
    """
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
    """ Nous redirige vers la page accueil après connexion
    """
    response = client.post(
        "/login/",
        data={"username": "clemence.bcq@gmail.com", "password": "1234"},
        follow_redirects=True, 
    )
    assert response.status_code == 200  

def test_login_failed(client):
    """ Nous redirige vers la page login
    """
    response = client.post("/login",data={"username":"clemence@gmail.com", "password":"4321"},
    follow_redirects=True,
    )
    assert response.status_code == 200 


@patch("mobilist.routes.views.current_user")
def test_protected_accueil_failed(mock_current_user, client):
    """Doit obtenir 302 puisque l'utilisateur se connecte avec un compte inexistant"""
    mock_current_user.is_authenticated = True
    mock_current_user.id_user = 1
    mock_current_user.username = "clemence@mail.com"

    response = client.get("/accueil-connexion/")
    assert response.status_code == 302


@patch("mobilist.routes.views.current_user")
def test_protected_accueil_success(mock_current_user, client):
    mock_current_user.is_authenticated = True
    mock_current_user.id_user = 2
    response = client.post("/login/", data={"mail":"trixymartin@email.com","password":"123","next":2, "id":2},follow_redirects=True)

    response = client.get("/accueil-connexion/")
    assert response.status_code == 200

@patch("mobilist.routes.views.current_user")
def test_protected_ajoutLogement_failed(mock_current_user, client):
    """renvoit vers la page actuel soit 200"""
    mock_current_user.is_authenticated = True
    mock_current_user.id_user = 2
    client.post("/login/", data={"mail":"trixymartin@email.com","password":"123","next":2, "id":2},follow_redirects=True)

    response = client.post("/logement/ajout", data={"name":"logement1", "typeL": "APPART", "address": "1 rue du pendu", "description": "", "rooms-array": "{'id': 'room-0', 'name': 'piece1', 'description': ''}"})
    assert response.status_code == 200

@patch("mobilist.routes.views.current_user")
def test_protected_ajoutLogement_success(mock_current_user, client):
    """Redirige vers une page soit 302 """
    mock_current_user.is_authenticated = True
    mock_current_user.id_user = 2
    client.post("/login/", data={"mail":"trixymartin@email.com","password":"123","next":2, "id":2},follow_redirects=True)

    response = client.post("/logement/ajout", data={"name":"logement1", "typeL": "APPART", "address": "1 rue du pendu", "description": "", "rooms-array": '[{"id": "room-0", "name": "piece1", "description": ""}]'})
    assert response.status_code == 302

@patch("mobilist.routes.views.current_user")
def test_protected_afficheLogements_failed(mock_current_user, client):
    mock_current_user.is_authenticated = True
    mock_current_user.id_user = 2
    client.post("/login/", data={"mail":"trixymartin@email.com","password":"123","next":2, "id":2},follow_redirects=True)

    response = client.get("/afficheLogements/")
    assert response.status_code == 200



@patch("mobilist.routes.views.current_user")
def test_protected_afficheLogements_success(mock_current_user, client):
    mock_current_user.is_authenticated = True
    mock_current_user.id_user = 2
    client.post("/login/", data={"mail":"trixymartin@email.com","password":"123","next":2, "id":2},follow_redirects=True)

    response = client.post("/afficheLogements/", data={"type-form":"UPDATE_LOGEMENT", "id":1, "name":"log1", "address":"14 rue du pendu", "description": "ajout d'une description","type": "APPART"})
    assert response.status_code == 200

    response = client.post("/afficheLogements/", data={"type-form":"DELETE_LOGEMENT", "id":1})
    assert response.status_code == 200

@patch("mobilist.routes.views.current_user")
def test_protected_ajouteBien_success(mock_current_user, client):
    mock_current_user.is_authenticated = True
    mock_current_user.id_user = 2
    client.post("/login/", data={"mail":"trixymartin@email.com","password":"123","next":2, "id":2},follow_redirects=True)

    response = client.post("/bien/ajout", data={"Logement":"logement1", "Nom du bien": "mon bien 1", "Type de bien":"Canapé", "Catégorie": "Décoration",'Nombre de pièces':"piece1", 'Prix neuf': 111, "Date de l'achat": "2020-20-12", "id_proprio": 2, "id_bien":2})
    assert response.status_code == 200


@patch("mobilist.routes.views.current_user")
def test_protected_mesBiens_success(mock_current_user, client):
    mock_current_user.is_authenticated = True
    mock_current_user.id_user = 2
    client.post("/login/", data={"mail":"trixymartin@email.com","password":"123","next":2, "id":2},follow_redirects=True)

    response = client.get("/mesBiens/", data={"id":"1"})
    assert response.status_code == 200


@patch("mobilist.routes.views.current_user")
def test_protected_modifierBien_success(mock_current_user, client):
    mock_current_user.is_authenticated = True
    mock_current_user.id_user = 2
    client.post("/login/", data={"mail":"trixymartin@email.com","password":"123","next":2, "id":2},follow_redirects=True)

    response = client.post("/modifierbien/", data={"id": 1, "nom_bien":"bien1", "logement":"logement1", "prix_bien":111, "date_bien": "2020-20-12", "categorie_bien": "Décoration", "type_bien": "Canapé"})
    assert response.status_code == 200

@patch("mobilist.routes.views.current_user")
def test_protected_simulation_success(mock_current_user, client):
    mock_current_user.is_authenticated = True
    mock_current_user.id_user = 2
    client.post("/login/", data={"mail":"trixymartin@email.com","password":"123","next":2, "id":2},follow_redirects=True)

    response = client.get("/simulation/",data={"logement_id": 1, "sinistre_annee": 2023, 'sinistre_type': 'Inondatation'})
    assert response.status_code == 200


@patch("mobilist.routes.views.current_user")
def test_protected_ensemblebiens_success(mock_current_user, client):
    mock_current_user.is_authenticated = True
    mock_current_user.id_user = 2
    client.post("/login/", data={"mail":"trixymartin@email.com","password":"123","next":2, "id":2},follow_redirects=True)

    response = client.get("/ensemblebiens/")
    assert response.status_code == 200

   