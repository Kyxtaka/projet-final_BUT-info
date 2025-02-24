from datetime import datetime
from flask import (
    flash, jsonify, 
    render_template, 
    send_file, redirect, 
    render_template, url_for, 
    render_template_string
    )
from mobilist.app import app
from mobilist.secure_constante import GOOGLE_SMTP, GOOGLE_SMTP_PWD, GOOGLE_SMTP_USER
from mobilist.models import *
from mobilist.exception import *
from mobilist.commands import create_user
from .login import login_view

from wtforms import PasswordField
from hashlib import sha256
from flask_login import login_user , current_user, AnonymousUserMixin
from flask import request
from flask_login import login_required
from mobilist.exception import *
from flask_wtf import FlaskForm
from wtforms import * #import de tous les champs
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
from werkzeug.datastructures import MultiDict
import json

import spacy
from PyPDF2 import PdfReader
import ast
import webbrowser
nlp = spacy.load("fr_core_news_md")

from .PDF.generatePDF import *
from .login.classes.ModificationForm import ModificationForm


# pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))


@app.route("/")
def home():
    return render_template('accueil.html')

@app.route("/accueil")
def accueil():
    return render_template('accueil.html')

@app.route("/avis")
def avis():
    return render_template("avis.html")

@app.route("/accueil-connexion/", methods =("GET","POST" ,))
@login_required   
def accueil_connexion():
    proprio = Proprietaire.query.get(current_user.id_user)
    logements = []
    infos, a_justifier = biens()
    for logement in proprio.logements:
        logements.append(logement)
    if request.method == 'POST':
        if 'bouton_telecharger' in request.form:
            return generate_pdf_tous_logements(proprio,logements)
    return render_template("accueil_2.html", infos=infos[:4], justifies=a_justifier[:4])
    
def biens():
    biens, justifies = User.get_biens_by_user(current_user.mail)
    infos = []
    for elem in biens:
        for j in range(len(elem)):
            bien = elem[j]
            justif = bien.get_justif(bien.id_bien)
            if justif == None:
                justif= "Aucun"
            infos.append([bien.nom_bien, bien.get_nom_logement_by_bien(bien.id_bien).nom_logement, bien.get_nom_piece_by_bien(bien.id_bien).nom_piece, str(bien.id_bien),justif])
    a_justifier = []
    for justifie in justifies:
        a_justifier.append([justifie.nom_bien, justifie.get_nom_logement_by_bien(justifie.id_bien).nom_logement, justifie.get_nom_piece_by_bien(justifie.id_bien).nom_piece, str(justifie.id_bien)])
    return infos, a_justifier

@app.route("/information")
def information():
    return render_template("information.html")

@app.route("/services")
def services():
    return render_template("services.html")

# Endpoint pour la page d'ajout de logement
# utilise la methode POST pour l'envoi de formulaire
# utilisation du json pour la reponse (standard pour les API)
# Permet de recuperer les pieces d'un logement
@app.route("/get_pieces/<int:logement_id>")
@login_required
def get_pieces(logement_id):
    pieces = Piece.query.filter_by(id_logement=logement_id).all()
    pieces_data = [{"id": piece.get_id_piece(), "name": piece.get_nom_piece()} for piece in pieces]
    return jsonify({"pieces": pieces_data})


@app.route("/ensemblebiens/", methods=["GET"])
@login_required
def ensemble_biens():
    info, justifie = biens()
    return render_template("ensemble_biens.html", infos=info, justifies=justifie)
    


@app.route("/afficheLogements/", methods=("GET", "POST",))
@login_required
def affiche_logements():
    session = db.session
    proprio = Proprietaire.query.get(current_user.id_user)
    logements = proprio.logements
    if len(logements) == 0:
        print("Aucun logement trouvé")
        contenu = False
    else:
        contenu = True
    type_logement = [type for type in LogementType]
    if request.method == "POST": #utilisation de request car pas envie d'utiliser les méthodes de flask, car j utilise JS
        print("recerption de la requete")
        form_type = request.form.get("type-form")
        print("form_type",form_type)
        match form_type:
            case "DELETE_LOGEMENT":
                try :
                    print("DELETE_LOGEMENT")
                    id_logement = request.form.get("id")
                    logement = Logement.query.get(id_logement)
                    logement.delete(Proprietaire.query.get(current_user.id_user))
                    session.commit()
                    print("Logement supprimé")
                except Exception as e:
                    session.rollback()
                    print("Erreur lors de la suppression du logement")
                    print(e)
            case "UPDATE_LOGEMENT":
                try:
                    print("UPDATE_LOGEMENT")
                    id_logement = request.form.get("id")
                    logement = Logement.query.get(id_logement)
                    print("logement recupere",logement)
                    name = request.form.get("name")
                    address = request.form.get("address")
                    description = request.form.get("description")
                    type = request.form.get("type")
                    enum_type = LogementType[type]
                    print("values",name,address,description, type, enum_type)
                    logement.set_nom_logement(name)
                    logement.set_adresse_logement(address)
                    logement.set_desc_logement(description)
                    logement.set_type_logement(enum_type)
                    print("logement apres modif",logement)
                    session.commit()
                    print("Logement modifié")
                except Exception as e:
                    session.rollback()
                    print("Erreur lors de la modification du logement")
                    print(e)
                # return render_template("updateLogement.html", logement=logement)
        proprio = Proprietaire.query.get(current_user.id_user)
        logements = proprio.logements
        return render_template("afficheLogements.html", logements=logements, type_logement=type_logement, contenu=contenu)
    return render_template("afficheLogements.html", logements=logements, type_logement=type_logement, contenu=contenu)

@app.route("/simulation/", methods =("GET","POST" ,))
def simulation():
    proprio = Proprietaire.query.get(current_user.id_user)
    logements = []
    for logement in proprio.logements:
        logements.append(logement)
    logement_id = request.form.get('logement_id')
    sinistre_annee = request.form.get('sinistre_annee')
    sinistre_type = request.form.get('sinistre_type')

    # Message d'erreur si tous les champs ne sont pas sélectionnés
    if request.method == "POST":
        if not logement_id or not sinistre_annee or not sinistre_type:
            message = "Veuillez sélectionner tous les champs."
            return render_template("simulation.html", logements=logements,
                                   message=message, logement_id=logement_id,
                                   sinistre_annee=sinistre_annee,
                                   sinistre_type=sinistre_type)
        return generate_pdf(proprio,logement_id,sinistre_annee,sinistre_type)
    return render_template("simulation.html",logements=logements)

@app.route("/mon-compte/", methods =("POST" ,"GET",))
def mon_compte():
    form = ModificationForm()
    if current_user.is_authenticated and current_user.proprio:
        form.nom.data = current_user.proprio.nom
        form.prenom.data = current_user.proprio.prenom
    if request.method == "POST":
        User.modifier(current_user.mail, request.form.get('nom'), request.form.get('prenom'))
        flash("Vos informations ont été mises à jour avec succès.", "success")
        return redirect(url_for('mon_compte'))
    return render_template("mon-compte.html", form=form)


@app.route("/mesBiens/", methods =["GET"])
def mesBiens():
    logement_id = request.args.get("logement")
    proprio = Proprietaire.query.get(current_user.id_user)
    logements = []
    for logement in proprio.logements:
        logements.append(logement)
    if logement_id:
        logement_actuel = int(logement_id)
        pieces = Piece.query.filter_by(id_logement=logement_actuel).all()
    else:
        logement_actuel = None
        pieces = []
    return render_template("mesBiens.html",logements=logements,logement_id=logement_id,pieces=pieces,logement_actuel=logement_actuel)


       
@app.route("/logement/ajout", methods =["GET","POST"])
def ajout_logement():
    if request.method == "POST":
        print("Ajout logement")
        print(f"form data: {request.form}")
        logement_name = request.form.get("name")
        logement_type = request.form.get("typeL")
        logement_address = request.form.get("address")
        logement_description = request.form.get("description")
        print(f"values: {logement_name}, {logement_type}, {logement_address}, {logement_description}")
        try: 
            proprio = Proprietaire.query.get(current_user.id_user)
            print(f"Proprio: {proprio}")

            new_logement = create_logement(logement_name, logement_type, logement_address, logement_description )

            link_logement_owner(new_logement, proprio)
            print(f"New logement: {new_logement}")

            rooms = json.loads(request.form.get("rooms-array"))
            print(f"Rooms: {rooms}")
            for room in rooms:
                print(f"setting room: {room}")
                ajout_piece_logement(new_logement, room["name"], room["description"])

            return redirect(url_for("accueil_connexion"))
        except Exception as e:
            print("Erreur lors de l'ajout du logement phase 1")
            print(e)
    return render_template("ajout_logement.html", type_logement=[type for type in LogementType])

def create_logement(name: str, type: str, address: str, description: str) -> Logement:
    session = db.session
    id_logement = Logement.next_id()
    print("id_logement:", id_logement)
    enum_type = LogementType[type]
    print("enum_type:", enum_type)
    new_logement = Logement(
        id_logement = id_logement,
        nom_logement = name,
        type_logement = enum_type,
        adresse_logement = address,
        desc_logement = description 
    )
    try:
        session.add(new_logement)
        session.commit()
        new_logement = Logement.query.get(id_logement)  
        print("Logement ajouté")
    except Exception as e:
        session.rollback()
        print("Erreur lors de l'ajout du logement phase 2")
        print(e)
    return new_logement

def ajout_piece_logement(Logement: Logement, room_name: str = "", desc: str = ""):
    session = db.session
    success = False
    try:
        id_piece = Piece.next_id()
        print(f"new piece id: {id_piece}")
        new_piece = Piece(
            id_piece=id_piece,
            nom_piece=room_name,
            desc_piece=desc,
            id_logement=Logement.get_id_logement()
        )
        session.add(new_piece)
        session.commit()
        print("Piece ajoutée")
        success = True
    except Exception as e:
        session.rollback()
        print("Erreur lors de l'ajout de la piece")
        print(e)
    return success

def link_logement_owner(logement: Logement, proprio: Proprietaire):
    session = db.session
    success = False
    try:
        link = AVOIR(
            id_proprio=proprio.get_id_proprio(),
            id_logement=logement.get_id_logement()
        )
        session.add(link)
        session.commit()
        print("Logement lié au propriétaire")
        success = True
    except Exception as e:
        session.rollback()
        print("Erreur lors de la liaison du logement au propriétaire")
        print(e)
    return success

@app.route("/test/")
def test():
    return render_template_string(str(Logement.next_id()))

def extraire_informations(texte):
    doc = nlp(texte)
    donnees = {"prix": "", "date_achat": ""}
    for ent in doc.ents:
        if ent.label_ == "PRIX":
            donnees["prix"] = ent.text
        elif ent.label_ == "DATE":
            donnees["date_achat"] = ent.text
    return donnees

    
@app.route("/open", methods=["GET"])
@login_required
def open_fic():
    url = request.args.get("url")
    # webbrowser.open('/'+url)
    return redirect(url_for('accueil_connexion'))
