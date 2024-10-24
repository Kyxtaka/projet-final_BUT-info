from .app import app, db
from .models import *
from datetime import *
import yaml
import click

#Commande de creation de table
@app.cli.command()
def syncdb():
    db.create_all()

#Commande de chargement de donnée via un fichier yml + creation tables
@app.cli.command()
@click.argument('filename')
def loaddb(filename):
    db.drop_all()
    db.create_all()
    data = yaml.load(open(filename), Loader=yaml.SafeLoader)
    session = db.session
    date_format = '%Y-%m-%d'
    for entity in data:
        match entity['TYPE']:
            case 'PROPRIETAIRE':
                new_proprietaire = Proprietaire(
                    id_proprio = entity['ID_PROPRIETAIRE'], 
                    nom_proprio = entity['NOM'],
                    prenom_proprio = entity['PRENOM'])
                session.add(new_proprietaire)
            case 'LOGEMENT':
                new_logement = Logement(
                    id_logement = entity['ID_LOGEMENT'],
                    type_logement = entity['TYPE_LOGEMENT'],
                    adresse_logement = entity['ADRESSE'],
                    desc_logement = entity['DESCRIPTION'])
                session.add(new_logement)
            case 'PIECE':
                new_piece = Piece(
                    id_piece = entity['ID_PIECE'],
                    nom_piece = entity['NOM_PIECE'],
                    desc_piece = entity['DESCRIPTION'],
                    id_logement = entity['ID_LOGEMENT']
                )
                session.add(new_piece)
            case 'CATEGORIE_BIEN':
                new_categorie = Categorie(
                    id_cat = entity['ID_CATEGORIE'],
                    nom_cat = entity['NOM_CATEGORIE']
                )
                session.add(new_categorie)
            case 'TYPE_BIEN':
                new_typeB = TypeBien(
                    id_type = entity['ID_TYPE'],
                    nom_type = entity['NOM_TYPE']
                )
                session.add(new_typeB)
            case 'BIEN':
                date = datetime.strptime(entity['DATE_ACHAT'], date_format)
                new_bien = Bien(
                    id_bien = entity['ID_BIEN'],
                    nom_bien = entity['NOM_BIEN'],
                    date_achat = date.date(),
                    prix = entity['PRIX'],
                    id_piece = entity['ID_PIECE'],
                    id_type = entity['ID_TYPE_BIEN'],
                    id_cat = entity['ID_CATEGORIE'],
                    id_proprio = entity['ID_PROPRIETAIRE']
                )
                session.add(new_bien)
            case 'JUSTIFICATIF':
                date = datetime.strptime(entity['DATE_AJOUT'], date_format)
                new_justificatif = Justificatif(
                    id_justif = entity['ID_JUSTIFICATIF'],
                    nom_justif = entity['NOM_JUSTIFICATIF'],
                    date_ajout = date,
                    URL = entity['URL'],
                    id_bien = entity['ID_BIEN']
                )
                session.add(new_justificatif)
            case 'AVIS':
                new_avis = Avis(
                    id_avis = entity['ID_AVIS'],
                    desc_avis = entity['DESCRIPTION'],
                    id_proprio = entity['ID_PROPRIETAIRE']
                )
                session.add(new_avis)
            case 'AVOIR':
                new_avoir = AVOIR(
                    id_proprio = entity['ID_PROPRIETAIRE'],
                    id_logement = entity['ID_LOGEMENT']
                )
                session.add(new_avoir)
        db.session.commit()
    print(f"loaded file: {filename}")

@app.cli.command()
@click.argument('mail')
@click.argument('password')
@click.argument('role')
def newuser(mail, password, role):
    from.models import User
    from hashlib import sha256
    m = sha256()
    m.update(password.encode())
    id = None
    if role != "admin":
        proprio = Proprietaire(idProprio=id)
        id = int(max_id())+1
        db.session.add(proprio)
    u = User(mail=mail, password=m.hexdigest(), role=role, id_user=id)
    db.session.add(u)
    db.session.commit()
    
@app.cli.command()
@click.argument('mail')
@click.argument('password')
def passwd(mail, password):
    from.models import User
    from hashlib import sha256
    m = sha256()
    m.update(password.encode())
    u = User.query.get(mail)
    u.password = m.hexdigest()
    db.session.commit()