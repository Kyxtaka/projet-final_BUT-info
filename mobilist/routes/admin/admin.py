from ...models.classes.Categorie import Categorie
from ...models.classes.Logement import Bien
from ...models.classes.Logement import AVOIR
from ...models.classes.Avis import Avis
import json
from flask import request
from ...app import db


from flask import Blueprint
from flask import (
    render_template, 
    render_template
    )

admin_bp = Blueprint('admin', __name__)


@admin_bp.route("/lesBiens/", methods=["GET", "POST"])
def lesBiens() -> str:
    """
    Affiche les caractèristiques des biens

    Returns :
        la page 'lesBiens' est affichée
    """
    all_categories = Categorie.get_all()
    if request.method == "POST":
        nom_cat = request.form.get('name')
        cat = Categorie(Categorie.max_id()+1, nom_cat)
        Categorie.put_categorie(cat)
        return render_template("lesBiens.html", cat=all_categories, notif= "1")
    return render_template("lesBiens.html", cat=all_categories, notif="0")


@admin_bp.route("/lesAvis/", methods=["GET", "POST"])
def lesAvis() -> str:
    """
    Affiche les avis

    Returns :
        la page 'lesAvis' est affichée
    """
    avis = Avis.get_all()
    if request.method == "POST":
        id_avis = request.form.get('value_avis')
        Avis.delete(id_avis)
        avis = Avis.get_all()
        return render_template("lesAvis-admin.html", avis=avis, notif="1")
    return render_template("lesAvis-admin.html", avis=avis, notif="0")



