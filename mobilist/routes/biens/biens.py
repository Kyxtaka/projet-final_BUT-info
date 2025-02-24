from flask import (
    render_template, 
    render_template
    )
from mobilist.models import *
from flask import Blueprint
from flask_login import current_user
from flask import request
from flask_login import login_required
from ..PDF.generatePDF import *


biens_bp = Blueprint('biens', __name__)
@biens_bp.route("/mesBiens/", methods =["GET"])
def mesBiens() -> str:
    """
    Affiche les biens et logements d'un propriétaire 

    Returns :
        la page 'mesBiens' est affichée
    """
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


@biens_bp.route("/simulation/", methods =("GET","POST" ,))
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
    """
    Récupère les informations des biens de l'utilisateur connecté
    """
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


