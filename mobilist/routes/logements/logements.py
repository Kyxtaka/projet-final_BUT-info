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
    flash, jsonify, 
    render_template, 
    send_file, redirect, 
    render_template, url_for, 
    render_template_string
    )
from flask import request
from flask_login import login_required
from flask_login import login_user, current_user
from ...app import db


logements_bp = Blueprint('logements', __name__)

@logements_bp.route("/afficheLogements/", methods=("GET", "POST",))
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
                # return render_template("updateLogement.html", logement=logement)
        proprio = Proprietaire.query.get(current_user.id_user)
        logements = proprio.logements
        return render_template("afficheLogements.html", logements=logements, type_logement=type_logement, contenu=contenu)
    return render_template("afficheLogements.html", logements=logements, type_logement=type_logement, contenu=contenu)


@logements_bp.route("/logement/ajout", methods =["GET","POST"])
@login_required
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

@logements_bp.route("/logement/manage_room/<int:id>", methods=["GET", "POST", "PUT", "DELETE"])
@login_required
def manage_room(id):
    print("id:", id)
    accessID = request.args.get("ClientID")
    print("accessID:", accessID)
    print("accessID:", accessID)
    print("current_user.id_user:", current_user.id_user)
    print(check_logement_access(id))
    if not check_logement_access(id):
        return redirect(url_for("accueil_connexion"))
    logement = Logement.query.get(id)
    if logement is None: return redirect(url_for("accueil_connexion"))
    try: 
        handle_manage_room_request(request, id) 
    except Exception as e:
        print("Erreur lors de la gestion de la pièce")
    pieces = Piece.query.filter_by(id_logement=id).all()
    print("pieces:", pieces)
    return render_template("manage_room.html", rooms=pieces, logement=logement)

def handle_manage_room_request(request, id):
    print("request.method:", request.method)
    print("handling ")
    match request.method:
        case "POST":
            room_name = request.form.get("roomName")
            room_desc = request.form.get("roomDesc")
            print("room_name:", room_name)
            print("room_desc:", room_desc)
            ajout_piece_logement(Logement.query.get(id), room_name, room_desc)
            return url_for("logements.manage_room", id=id)
        
        case "PUT": 
            print("PUT")
            print("request.form:", request.form)
            room_id = request.form.get("roomId")
            room_name = request.form.get("roomName")
            room_desc = request.form.get("roomDesc")
            print("room_id:", room_id)
            print("room_name:", room_name)
            print("room_desc:", room_desc)
            return url_for("manage_room", id=id)
        
        case "DELETE": 
            deleted_item_id= request.args.get("roomId")
            try: 
                piece = Piece.query.get((deleted_item_id, request.args.get("logementId")))
                
                db.session.delete(piece)
                db.session.commit()
                print("Piece supprimée")
            except Exception as e:
                db.session.rollback()
                print("Erreur lors de la suppression de la pièce")
                print(e)


def check_logement_access(id):
    result = False
    try:
        logement = Logement.query.get(id)
        proprio = Proprietaire.query.get(current_user.id_user)
        if logement in proprio.logements:
            result = True
        else:
            result = False
    except Exception as e:
        print("Erreur lors de la vérification de l'accès au logement")
    return result

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


@logements_bp.route("/get_pieces/<int:logement_id>")
@login_required
def get_pieces(logement_id):
    pieces = Piece.query.filter_by(id_logement=logement_id).all()
    pieces_data = [{"id": piece.get_id_piece(), "name": piece.get_nom_piece()} for piece in pieces]
    return jsonify({"pieces": pieces_data})