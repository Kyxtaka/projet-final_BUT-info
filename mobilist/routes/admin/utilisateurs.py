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
@login_required
def lesUtilisateurs() -> str:
    """
    Affiche les utilisateurs

    Returns :
        la page 'lesUtilisateurs' est affichée
    """
    form = RechercheForm()
    form_inscription = InscriptionForm()

    # barre de recherche
    if form.is_submitted() and form.validate_on_submit():
        proprio = form.champ.data
        res_recherche = Proprietaire.get_by_nom_sans_casse(proprio)
        res_recherche = list(res_recherche) 
        if not res_recherche:
            res_recherche_triee = None
        else:
            res_recherche_triee = sorted(res_recherche, key=lambda personne: (personne.nom.lower(), personne.prenom.lower()))
        print(res_recherche)
        return render_template("lesUtilisateurs.html", form = form, res_recherche = res_recherche_triee, form_inscription = form_inscription)
        
    # inscrire un utilisateur
    if "inscription_submit" in request.form:
        if form_inscription.is_submitted() and form_inscription.validate_on_submit():
            user_existant = User.query.filter_by(mail=form_inscription.mail.data).first()
            if user_existant:
                login_user(user_existant)
                flash("Ce compte existe déjà.", "error")
                return redirect(url_for('utilisateurs.lesUtilisateurs'))
            create_user(form_inscription.mail.data, form_inscription.password.data, "proprio")
            User.modifier(form_inscription.mail.data, form_inscription.nom.data, form_inscription.prenom.data)
            flash("Utilisateur ajouté avec succès!", "success")
            return redirect(url_for('utilisateurs.lesUtilisateurs'))
     
    proprios = Proprietaire.get_all()
    proprios_triee = sorted(proprios, key=lambda personne: (personne.nom.lower(), personne.prenom.lower()))

    return render_template("lesUtilisateurs.html", form = form, proprios = proprios_triee, form_inscription = form_inscription)

@utilisateur_bp.route("/supprimer_utilisateur/", methods=("GET", "POST",))
@login_required
def supprimer_utilisateur():
    """
    Supprime un utilisateur 
    """
    if "supprimer_submit" in request.form:
        utilisateur_id = request.form.get('utilisateur_id')
        if utilisateur_id:
            utilisateur = Proprietaire.query.get_or_404(utilisateur_id)
            user = User.query.get_or_404(utilisateur.get_mail())
            db.session.delete(utilisateur)
            db.session.delete(user)
            db.session.commit()
            flash("Utilisateur supprimé avec succès!", "success")
        else:
            flash('Utilisateur non trouvé', 'error')
    return redirect(url_for('utilisateurs.lesUtilisateurs'))
