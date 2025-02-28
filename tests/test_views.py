import os
import tempfile
from flask import Flask
from flask_sqlalchemy  import SQLAlchemy
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
from mobilist.models.classes.Logement import *
from mobilist.routes.uploadfile.classes.AjoutBienForm import AjoutBienForm
from mobilist.routes.uploadfile.classes.UploadFileForm import UploadFileForm
from mobilist.routes.uploadfile.upload import handle_form_bien, link_justification_bien, form_logs
from mobilist.routes.admin.utilisateurs import *
from mobilist.routes.login.login_view import *
from mobilist.routes.login.classes.InscriptionForm import InscriptionForm
from mobilist.routes.biens.biens import *
from mobilist.exception import DejaPresent
import datetime
from flask import session
import pytest
import os
from mobilist.app import mkpath, app, db
from unittest.mock import MagicMock
from hashlib import sha256
from unittest.mock import patch
from mobilist.models.classes.Proprietaire import Proprietaire  


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
def test_protected_ajouteBien_success(mock_current_user, client,monkeypatch):
    mock_current_user.is_authenticated = True
    mock_current_user.id_user = 2
    client.post("/login/", data={"mail":"trixymartin@email.com","password":"123","next":2, "id":2},follow_redirects=True)
    form = MagicMock(spec=AjoutBienForm)
    form.validate()

    form.nom_bien.data = "bien1"
    form.date_bien.data = datetime.date(2024, 11, 12)
    form.id_proprio = 2
    form.prix_bien.data = 111
    form.piece_bien.data = 1
    form.logement.data = 1
    form.type_bien.data = 1
    form.categorie_bien.data = 1

    monkeypatch.setattr('mobilist.routes.uploadfile.classes', form)

    response = client.post("/bien/ajout", data={"Logement":"logement1", "Nom du bien": "mon bien 1", "Type de bien":"Canapé", "Catégorie": "Décoration",'Nombre de pièces':"piece1", 'Prix neuf': 111, "Date de l'achat": "2020-20-12", "id_proprio": 2, "id_bien":2})
    assert response.status_code == 200

@patch("mobilist.routes.views.current_user")
def test_fonctions_upload(mock_current_user, client):
    mock_current_user.is_authenticated = True
    mock_current_user.id_user = 2
    client.post("/login/", data={"mail":"trixymartin@email.com","password":"123","next":2, "id":2},follow_redirects=True)
    form = MagicMock(spec=AjoutBienForm)
    form.validate()

    form.nom_bien.data = "bien1"
    form.date_bien.data = datetime.date(2024, 11, 12)
    form.id_proprio = 2
    form.prix_bien.data = 111
    form.piece_bien.data = 1
    form.logement.data = 1
    form.type_bien.data = 1
    form.categorie_bien.data = 1

    handle_form_bien(form)
    link_justification_bien(form, 'document_test/inventaires_biens-1.pdf', 1)
    form_logs(form)
    

@patch("mobilist.routes.views.current_user")
def test_protected_mesBiens_success(mock_current_user, client):
    mock_current_user.is_authenticated = True
    mock_current_user.id_user = 2
    client.post("/login/", data={"mail":"trixymartin@email.com","password":"123","next":2, "id":2},follow_redirects=True)

    response = client.get("/mesBiens/", data={"id":"1"})
    assert response.status_code == 200


@patch("mobilist.routes.views.current_user")
def test_protected_modifierBien_success(mock_current_user, client,monkeypatch):
    mock_current_user.is_authenticated = True
    mock_current_user.id_user = 2
    client.post("/login/", data={"mail":"trixymartin@email.com","password":"123","next":2, "id":2},follow_redirects=True)
    form = MagicMock(spec=AjoutBienForm)
    form.validate()

    form.nom_bien.data = "bien1"
    form.date_bien.data = datetime.date(2024, 11, 12)
    form.id_proprio = 2
    form.prix_bien.data = 111
    form.piece_bien.data = 1
    form.logement.data = 1
    form.type_bien.data = 1
    form.categorie_bien.data = 1

    monkeypatch.setattr('mobilist.routes.uploadfile.classes.AjoutBienForm', form)

    bien = Bien(3,"chaise",2,datetime.date(2024, 11, 12), 19.99, 1,1,1,1)
    Bien.put_bien(bien)

    response = client.post("/modifierbien/", data={"id": 3, "nom_bien":"bien1", "logement":"logement1", "prix_bien":111, "date_bien": "2020-20-12", "categorie_bien": "Décoration", "type_bien": "Canapé"})
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

@patch("mobilist.routes.views.current_user")
def test_protected_admin_biens(mock_current_user, client):
    mock_current_user.is_authenticated = True
    mock_current_user.id_user = 3
    client.post("/login/", data={"mail":"admin@mail.com","password":"123","next":4, "id":3},follow_redirects=True)

    response = client.get("/lesBiens/")
    assert response.status_code == 200

    response = client.post("/lesBiens/", data={'name': 'Téléphonie'})
    assert response.status_code == 200


@patch("mobilist.routes.views.current_user")
def test_protected_admin_avis(mock_current_user, client):
    mock_current_user.is_authenticated = True
    mock_current_user.id_user = 3
    client.post("/login/", data={"mail":"admin@mail.com","password":"123","next":4, "id":3},follow_redirects=True)

    response = client.get("/lesAvis/")
    assert response.status_code == 200

    response = client.post("/lesAvis/", data={'value_avis': '1'})
    assert response.status_code == 200


@patch("mobilist.routes.views.current_user")
def test_protected_admin_user(mock_current_user, client):
    mock_current_user.is_authenticated = True
    mock_current_user.id_user = 3
    client.post("/login/", data={"mail":"trixymartin@email.com","password":"123","next":2, "id":2},follow_redirects=True)

    response = client.post("/lesUtilisateurs/")
    assert response.status_code == 200

    response = client.post("/lesUtilisateurs/", data={'champ':'champ','recherche':''})
    assert response.status_code == 200

@patch("mobilist.routes.views.current_user")
def test_protected_admin_user_suppression(mock_current_user, client):
    mock_current_user.is_authenticated = True
    mock_current_user.id_user = 3
    client.post("/login/", data={"mail":"trixymartin@email.com","password":"123","next":2, "id":2},follow_redirects=True)

    User.put_user(User('test1@mail.com','123', 'admin',4))
    response = client.post("/supprimer_utilisateur/", data={'supprimer_submit': True, 'utilisateur_id':4})
    assert response.status_code == 302

@patch("mobilist.routes.views.current_user")
def test_protected_admin_user_inscription(mock_current_user, client):
    mock_current_user.is_authenticated = True
    mock_current_user.id_user = 3
    client.post("/login/", data={"mail":"trixymartin@email.com","password":"123","next":2, "id":2},follow_redirects=True)

    response = client.get("/lesUtilisateurs/", data={'inscription_submit': True})

    pwd_email('test1@mail.com', '123')
    set_mdp()

@patch("mobilist.routes.views.current_user")
def test_protected_admin_accueil(mock_current_user, client):
    mock_current_user.is_authenticated = True
    mock_current_user.id_user = 3
    client.post("/login/", data={"mail":"trixymartin@email.com","password":"123","next":2, "id":2},follow_redirects=True)

    response = client.get('/accueil-admin/')
    assert response.status_code == 200

@patch("mobilist.routes.views.current_user")
def test_protected_manage_rooms(mock_current_user, client):
    mock_current_user.is_authenticated = True
    mock_current_user.id_user = 2
    client.post("/login/", data={"mail":"trixymartin@email.com","password":"123","next":2, "id":2},follow_redirects=True)

    response = client.post("/logement/manage_room/2",data={'ClientID': 2,})
    assert response.status_code == 200

    response = client.post("/logement/manage_room/1",data={'ClientID': 2,})
    assert response.status_code == 302

@patch("mobilist.routes.views.current_user")
def test_protected_manage_rooms_put(mock_current_user, client):
    mock_current_user.is_authenticated = True
    mock_current_user.id_user = 2
    client.post("/login/", data={"mail":"trixymartin@email.com","password":"123","next":2, "id":2},follow_redirects=True)

    response = client.put("/logement/manage_room/2",data={'ClientID': 2,'logementId':2, 'roomId':3,'roomName':'piece', 'roomDesc':'description'})
    assert response.status_code == 200


@patch("mobilist.routes.views.current_user")
def test_protected_manage_rooms_delete(mock_current_user, client):
    mock_current_user.is_authenticated = True
    mock_current_user.id_user = 2
    client.post("/login/", data={"mail":"trixymartin@email.com","password":"123","next":2, "id":2},follow_redirects=True)

    response = client.delete("/logement/manage_room/2",data={'ClientID': 2,})
    assert response.status_code == 200

@patch("mobilist.routes.views.current_user")
def test_protected_set_password(mock_current_user, client):
    """Ne doit pas passer, le token n'existe pas"""
    mock_current_user.is_authenticated = True
    mock_current_user.id_user = 2
    client.post("/login/", data={"mail":"trixymartin@email.com","password":"123","next":2, "id":2},follow_redirects=True)

    response = client.get('/forgotPassword/setPassword', data={'token':'123'})
    assert response.status_code == 401
    response = client.post('/forgotPassword/setPassword', data={'token':'123'})
    assert response.status_code == 401

    send_change_pwd_email('clemence@mail.com', '123')


@patch("mobilist.routes.views.current_user")
def test_protected_page_oublie(mock_current_user, client, monkeypatch):
    
    mock_current_user.is_authenticated = True
    mock_current_user.id_user = 2
    client.post("/login/", data={"mail":"trixymartin@email.com","password":"123","next":2, "id":2},follow_redirects=True)

    form = MagicMock()
    form.validate()
    monkeypatch.setattr('mobilist.routes.login.classes.ResetForm.ResetForm', lambda: form) 
    form.email.data = "trixymartin@email.com"

    response = client.get('/forgotPassword/')
    assert response.status_code == 200


@patch("mobilist.routes.views.current_user")
def test_protected_inscription(mock_current_user, client):
    response = client.get('/inscription/')
    assert response.status_code == 200

@patch("mobilist.routes.views.current_user")
def test_protected_modifier_mdp(mock_current_user, client):
    mock_current_user.is_authenticated = True
    mock_current_user.id_user = 2
    client.post("/login/", data={"mail":"trixymartin@email.com","password":"123","next":2, "id":2},follow_redirects=True)
    
    response = client.post('/modif_mdp/',data={ 'mdp_actuel': '123', 'mdp':'1234', 'mdp_confirm':'1234'})
    assert response.status_code == 302

@patch("mobilist.routes.views.current_user")
def test_protected_telecharger(mock_current_user, client):
    mock_current_user.is_authenticated = True
    mock_current_user.id_user = 2
    mock_current_user.mail = "trixymartin@email.com"
    client.post("/login/", data={"mail":"trixymartin@email.com","password":"1234","next":2, "id":2},follow_redirects=True)

    response = client.post('/accueil-connexion/',data={ 'bouton_telecharger':'123'})
    assert response.status_code == 200


@patch("mobilist.routes.views.current_user")
def test_protected_compte(mock_current_user, client):
    mock_current_user.is_authenticated = True
    mock_current_user.id_user = 2
    mock_current_user.mail = "trixymartin@email.com"
    client.post("/login/", data={"mail":"trixymartin@email.com","password":"1234","next":2, "id":2},follow_redirects=True)

    response = client.get('/mon-compte/')
    assert response.status_code == 200

@patch("mobilist.routes.views.current_user")
def test_protected_compte_post(mock_current_user, client):
    mock_current_user.is_authenticated = True
    mock_current_user.id_user = 2
    mock_current_user.mail = "trixymartin@email.com"
    client.post("/login/", data={"mail":"trixymartin@email.com","password":"1234","next":2, "id":2},follow_redirects=True)

    response = client.post('/mon-compte/', data={'nom': 'martin','prenom':'prenom'})
    assert response.status_code == 302


@patch("mobilist.routes.views.current_user")
def test_protected_open(mock_current_user, client):
    mock_current_user.is_authenticated = True
    mock_current_user.id_user = 2
    client.post("/login/", data={"mail":"trixymartin@email.com","password":"1234","next":2, "id":2},follow_redirects=True)

    response = client.get('/open', data={"url":"url"})
    assert response.status_code == 302

@patch("mobilist.routes.views.current_user")
def test_protected_ajout_avis(mock_current_user, client):
    mock_current_user.is_authenticated = True
    mock_current_user.id_user = 2
    mock_current_user.proprio = Proprietaire(5,"trixymartin@email.com", "martin", "trixy")
    client.post("/login/", data={"mail":"trixymartin@email.com","password":"1234","next":2, "id":2},follow_redirects=True)

    response = client.post('/ajout_avis/', data={"avis":"mon avis"})
    assert response.status_code == 302

@patch("mobilist.routes.views.current_user")
def test_protected_uploadfileform(mock_current_user, client):
    mock_current_user.is_authenticated = True
    mock_current_user.id_user = 3
    client.post("/login/", data={"mail":"trixymartin@email.com","password":"123","next":2, "id":2},follow_redirects=True)

    file = UploadFileForm()
    file.file.data = 'document_test/inventaires_biens-1.pdf'
    file.validate()
    file.validate_file_format("form", file.file)


@patch("mobilist.routes.views.current_user")
def test_protected_movebien(mock_current_user, client):
    mock_current_user.is_authenticated = True
    mock_current_user.id_user = 3
    client.post("/login/", data={"mail":"trixymartin@email.com","password":"123","next":2, "id":2},follow_redirects=True)

    moveBiens(1, 1, 2)

@patch("mobilist.routes.views.current_user")
def test_exception(mock_current_user, client):
    test = DejaPresent("test")
    assert test.message == "test"

@patch("mobilist.routes.views.current_user")
def test_inscription(mock_current_user, client):
    with app.app_context():
        form = InscriptionForm()
        form.mail.data = "inconnu@email.com"

        assert form.get_authenticated_user() == None

@patch("mobilist.routes.views.current_user")
def test_ajoutform(mock_current_user, client):
    with app.app_context():
        mock_current_user.is_authenticated = True
        mock_current_user.id_user = 3
        client.post("/login/", data={"mail":"trixymartin@email.com","password":"1234","next":2, "id":2},follow_redirects=True)

        form = AjoutBienForm()
        form.set_id(2)
        assert form.get_log_choices('logement') == ""
        assert form.get_type_bien_choices('piece') == ""
        assert form.get_cat_bien_choices('cat') == ""
    
    

