from flask import (
    render_template, 
    render_template
    )
from ...models.classes.User import User
from ...models.classes.TypeBien import TypeBien
from ...models.classes.Proprietaire import Proprietaire
from ...models.classes.Logement import Piece
from ...models.classes.Logement import LogementType
from ...models.classes.Logement import Logement
from ...models.classes.Justificatif import Justificatif
from ...models.classes.Categorie import Categorie
from ...models.classes.Logement import Bien
from ...models.classes.Logement import AVOIR
from ...models.classes.Avis import Avis
from flask import Blueprint
from flask_login import current_user
from flask import request
from flask_login import login_required
from ..PDF.generatePDF import *


biens_bp = Blueprint('biens', __name__)
@biens_bp.route("/mesBiens/", methods =["GET", "POST", "DELETE", "PUT"])
@login_required
def mesBiens() -> str:
    """
    Affiche les biens et logements d'un propriétaire 

    Returns :
        la page 'mesBiens' est affichée
    """
    logement_id = request.args.get("logement")
    proprio = Proprietaire.query.get(current_user.id_user)
    logements = []
    if request.method == "DELETE" and request.args.get("logement") != None:
        print("DELETE")
        deleteBiens(request, request.args.get("logement"))
    if request.method == "PUT" and request.args.get("logement"):
        print("PUT")
        print(request.get_json())
        logementID =  request.args.get("logement")
        data = request.get_json()
        for d in data:
            moveBiens(logementID, d["id_piece"], d["id_bien"])
    for logement in proprio.logements:
        logements.append(logement)
    if logement_id:
        logement_actuel = int(logement_id)
        pieces = Piece.query.filter_by(id_logement=logement_actuel).all()
    else:
        logement_actuel = None
        pieces = []
    return render_template("mesBiens.html",logements=logements,logement_id=logement_id,pieces=pieces,logement_actuel=logement_actuel)

def deleteBiens(request, logement_id):
    data_json = request.get_json()
    print(data_json)
    for data in data_json:
        print(data)
        bien = Bien.query.get(data["id"])
        bien.delete()
        db.session.commit()
    return 

def moveBiens(logement_id, piece_id, bien_id):
    print("étape 3")
    try:
        bien = Bien.query.get(bien_id)
        bien.set_id_piece(piece_id) 
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
    print("étape 4")
    return


@biens_bp.route("/simulation/", methods =("GET","POST" ,))
@login_required
def simulation() -> str:
    """
    Permet de faire une simulation de sinistre pour un logement et de génèrer un inventaire

    Return :
        la page simulation est affichée
    """
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


@biens_bp.route("/ensemblebiens/", methods=["GET"])
@login_required
def ensemble_biens():
    """
    Affiche l'ensemble des biens d'un propriétaire

    Return :
        la page 'ensemble_bien' est affichée
    """
    info, justifie = biens()
    return render_template("ensemble_biens.html", infos=info, justifies=justifie)

def biens():
    biens, justifies = Bien.get_biens_by_user(current_user.mail)
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

