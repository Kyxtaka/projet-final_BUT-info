
from flask_wtf import FlaskForm
from mobilist.models import *
import os
import spacy
from PyPDF2 import PdfReader
import ast
import webbrowser
nlp = spacy.load("fr_core_news_md")
from reportlab.pdfgen import canvas #pip install reportlab
from datetime import datetime, date
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from .classes.UploadFileForm import UploadFileForm, UPLOAD_FOLDER_JUSTIFICATIF
from .classes.AjoutBienForm import AjoutBienForm
from flask_login import login_user , current_user, AnonymousUserMixin
from flask import request
from flask_login import login_required

from flask import Blueprint
from flask import (
    flash, jsonify, 
    render_template, 
    send_file, redirect, 
    render_template, url_for, 
    render_template_string
    )


upload_bp = Blueprint('upload', __name__)

@upload_bp.route("/bien/ajout", methods=("GET", "POST",))
@login_required
def ajout_bien():
    form_bien = AjoutBienForm()
    if form_bien.validate_on_submit():
        try:
            print("Logs:", form_logs(form_bien))
            handle_form_bien(form_bien)
            return redirect(url_for("accueil_connexion"))
        except Exception as e:
            print("error ajout bien")
            print("Logs:", form_logs(form_bien))
            return render_template("ajout_bien.html",
                               form=form_bien,
                               error=True)
    return render_template("ajout_bien.html",
                            form=form_bien,
                            error=False)

def handle_form_bien(form_bien: AjoutBienForm):
    try:
        session = db.session

        id_bien = Bien.next_id()+1
        nom_bien = form_bien.nom_bien.data
        date_achat = form_bien.date_bien.data
        id_proprio =  form_bien.id_proprio
        prix = form_bien.prix_bien.data
        id_piece = form_bien.piece_bien.data
        id_logement = form_bien.logement.data
        id_type = form_bien.type_bien.data
        id_cat = form_bien.categorie_bien.data
        nouv_bien = Bien(
            id_bien=id_bien,
            nom_bien=nom_bien,
            date_achat=date_achat,
            prix=prix,
            id_proprio=id_proprio,
            id_piece=id_piece,
            id_logement=id_logement,
            id_type=id_type,
            id_cat=id_cat)
        session.add(nouv_bien)
        session.commit()
        if form_bien.file.data:
            file_path = form_bien.create_justificatif_bien()
            print("file path:", file_path)
            process = link_justification_bien(form_bien, file_path, id_bien)
            if not process:
                raise Exception("Erreur lors de l'ajout du justificatif")
            else:
                print("Justificatif ajouté")
    except Exception as e:
        session.rollback() # afin d eviter les erreurs de commit si une erreur est survenue
        print("Logs:", form_logs(form_bien)) # affichage des logs
        print("Exception:", e)

def link_justification_bien(form: AjoutBienForm, file_path: str, id_bien: int) -> bool:
    session = db.session
    file = form.file.data
    id_justificatif = Justificatif.next_id()
    nom_justificatif = file.filename
    date_ajout = date.today()
    url = file_path
    id_bien = id_bien
    try:
        new_justificatif = Justificatif(
            id_justif=id_justificatif,
            nom_justif=nom_justificatif,
            date_ajout=date_ajout,
            URL=url,
            id_bien=id_bien
        )
        session.add(new_justificatif)
        session.commit()
    except Exception as e:
        session.rollback()
        print("Erreur lors de l'ajout du justificatif")
        print("Exception:", e)
        return False
    return True

def form_logs(form: FlaskForm):
    print("form sumbited:",form.is_submitted())
    print("form value valid:",form.validate_on_submit())
    if isinstance(form, AjoutBienForm):
        print("Ajout bien form detected")
        if form.file.data:
            print("file name:", form.file.data.filename)
            print("file data:", form.file.data)
        else:
            print("file data is empty")
    print("form errors:",form.errors)
    print("form data:", form.data)

@upload_bp.route("/modifierbien/", methods=["POST", "GET"])
def modifier_bien():
    id = request.values.get("id")
    bien = Bien.get_data_bien(id)
    form_bien = AjoutBienForm()

    if request.method == "GET":
        form_bien.set_id(id)
        form_bien.prix_bien.data = bien.prix
        form_bien.nom_bien.data = bien.nom_bien
        form_bien.logement.data = form_bien.get_log_choices(bien.get_typelogement(bien).nom_logement)
        form_bien.categorie_bien.data = form_bien.get_cat_bien_choices(bien.get_catbien(bien).nom_cat)
        form_bien.type_bien.data = form_bien.get_type_bien_choices(bien.get_typebien(bien).nom_type)
        
    if request.method == "POST" and form_bien.validate_on_submit():
        try:
            nom = request.form.get("nom_bien")
            logement = request.form.get("logement")
            prix = request.form.get("prix_bien")
            date = request.form.get("date_bien")
            categorie = request.form.get("categorie_bien")
            type_b = request.form.get("type_bien")
            Bien.modifier_bien(
                int(id), 
                nom,
                int(logement),
                float(prix),
                date, 
                int(categorie), 
                int(type_b)
                ) 
            return redirect(url_for("accueil_connexion"))
        except Exception as e:
            print(e)
            return render_template("modification_bien.html", 
                               form=form_bien,     
                               error=True)
    return render_template("modification_bien.html", 
                            form=form_bien, 
                            error=False)

                            