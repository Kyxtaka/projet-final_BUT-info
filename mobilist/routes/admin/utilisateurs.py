from flask import flash
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
from .classes.recherche import RechercheForm
from ..login.classes.InscriptionForm import InscriptionForm
from mobilist.commands import create_user

import json

from flask import Blueprint
from flask import (
    jsonify, 
    render_template, 
    redirect, 
    render_template, url_for
    )
from flask import request
from flask_login import login_required
from flask_login import login_user, current_user
from ...app import db

utilisateur_bp = Blueprint('utilisateurs', __name__)


@utilisateur_bp.route("/lesUtilisateurs/", methods=("GET", "POST",))
def lesUtilisateurs() -> str:
    """
    Affiche les utilisateurs

    Returns :
        la page 'lesUtilisateurs' est affichée
    """
    form = RechercheForm()
    form_inscription = InscriptionForm()
    if form.is_submitted() and form.validate_on_submit():
        proprio = form.champ.data
        res_recherche = Proprietaire.get_by_nom(proprio)
        return render_template("lesUtilisateurs.html", form = form, res_recherche = res_recherche, form_inscription = form_inscription)
    if form_inscription.is_submitted() and form_inscription.validate_on_submit():
        user = form_inscription.get_authenticated_user()
        if user:
            login_user(user)
            flash("Ce compte existe déjà.", "error")
            return render_template("lesUtilisateurs.html",form = form, form_inscription = form_inscription, present=True)
        create_user(form_inscription.mail.data, form_inscription.password.data, "proprio")
        User.modifier(form_inscription.mail.data, form_inscription.nom.data, form_inscription.prenom.data)
        flash("Utilisateur ajouté avec succès!", "success")
        return redirect(url_for('utilisateurs.lesUtilisateurs'))
    proprios = Proprietaire.get_all()
    return render_template("lesUtilisateurs.html", form = form, proprios = proprios, form_inscription = form_inscription)
