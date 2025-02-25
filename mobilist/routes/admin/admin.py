
from flask import Blueprint
from flask import (
    render_template, 
    render_template
    )


admin_bp = Blueprint('admin', __name__)


@admin_bp.route("/lesBiens/")
def lesBiens() -> str:
    """
    Affiche les caractèristiques des biens

    Returns :
        la page 'lesBiens' est affichée
    """
    return render_template("lesBiens.html")


@admin_bp.route("/lesAvis/")
def lesAvis() -> str:
    """
    Affiche les avis

    Returns :
        la page 'lesAvis' est affichée
    """
    return render_template("lesAvis-admin.html")