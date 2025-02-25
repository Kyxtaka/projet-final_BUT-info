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


@utilisateur_bp.route("/lesUtilisateurs/")
def lesUtilisateurs() -> str:
    """
    Affiche les utilisateurs

    Returns :
        la page 'lesUtilisateurs' est affichée
    """
    return render_template("lesUtilisateurs.html")


