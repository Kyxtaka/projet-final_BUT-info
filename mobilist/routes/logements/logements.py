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


logements_bp = Blueprint('logements', __name__)

@logements_bp.route("/afficheLogements/", methods=("GET", "POST",))
@login_required
def affiche_logements() -> str:
    """
    Fonction qui permet à un utilisateur de voir ses logements, de les supprimer ou de les modifier

    Returns :
        - Si la méthode est GET : la page avec la liste des logements du propriétaire est affichée
        - Si la méthode est POST : après la suppression ou la modification d'un logement, la page avec la mise à jour de la liste des logements est affichée
    """
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
        print("réception de la requete")
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
        proprio = Proprietaire.query.get(current_user.id_user)
        logements = proprio.logements
        return render_template("afficheLogements.html", logements=logements, type_logement=type_logement, contenu=contenu)
    return render_template("afficheLogements.html", logements=logements, type_logement=type_logement, contenu=contenu)


@logements_bp.route("/logement/ajout", methods =["GET","POST"])
def ajout_logement() -> str:
    """
    Fonction qui permet d'ajouter un nouveau logement

    Returns :
        - Si la méthode est GET : le formulaire d'ajout d'un logement est affiché
        - Si la méthode est POST : l'utilisateur est redirigé vers la page d'accueil après l'ajout du logement et des pièces
    """
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
    """
    Fonction qui permet de créer un nouveau logement en l'ajouter à la base de données

    Args :
        name (str) : le nom du logement
        type (str) : le type du logement
        address (str) : l'adresse du logement
        description (str) : la description du logement

    Returns : 
        (Logement) : le nouvel logement créé
    """
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

def ajout_piece_logement(Logement: Logement, room_name: str = "", desc: str = "") -> bool:
    """
    Fonction qui permet d'ajouter une nouvelle pièce à un logement

    Args :
        Logement (Logement) : le logement auquel la pièce doit être ajoutée
        room_name (str) : le nom de la pièce, une chaîne vide par défaut
        desc (str) : la description de la pièce, une chaîne vide par défaut

    Returns :
        (bool) : 'True' si la pièce a été ajoutée avec succès, 'False' si non

    """
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
    """
    Relie un logement à un propriétaire dans la base de données

    Args :
        logement (Logement) : le logement
        proprio (Proprietaire) : le propriétaire

    Return :
        (bool) : 'True' si la liaison a été effectuée avec succès, 'False' si non
    """
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


@logements_bp.route("/get_pieces/<int:logement_id>")
@login_required
def get_pieces(logement_id):
    """
    Récupère toutes les pièces d'un logement donné et les renvoie sous forme d'un JSON

    Args :
        logement_id (int) : l'ID du logement

    Return :
        (json) : un JSON avec la liste des pièces associées au logement, avec pour chaque pièce son 'id' et son 'name'
    """
    pieces = Piece.query.filter_by(id_logement=logement_id).all()
    pieces_data = [{"id": piece.get_id_piece(), "name": piece.get_nom_piece()} for piece in pieces]
    return jsonify({"pieces": pieces_data})