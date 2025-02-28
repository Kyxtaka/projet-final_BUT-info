# Importations de modules
from flask import (
    flash,
    render_template, 
    redirect, 
    render_template, url_for, 
    render_template_string
    )
from mobilist.app import app


from mobilist.exception import *

from flask_login import current_user
from flask import request
from flask_login import login_required
from mobilist.exception import *
import spacy
nlp = spacy.load("fr_core_news_md")

from .PDF.generatePDF import *
from .biens.biens import *
from .logements.logements import *
from .login.classes.ModificationForm import ModificationForm


@app.route("/")
def home():
    """
    Renvoie la page d'accueil du site
    """
    return render_template('accueil.html')

@app.route("/accueil")
def accueil():
    """
    Renvoie la page d'accueil du site
    """
    return render_template('accueil.html')

@app.route("/avis")
def avis():
    """
    Renvoie la page 'avis' du site
    """
    return render_template("avis.html")

@app.route("/accueil-connexion/", methods =("GET","POST" ,))
@login_required   
def accueil_connexion():
    """
    Renvoie la page d'accueil une fois connecté, et/ou génère un inventaire
    """
    proprio = Proprietaire.query.get(current_user.id_user)
    logements = []
    infos, a_justifier = biens()
    for logement in proprio.logements:
        logements.append(logement)
    if request.method == 'POST':
        if 'bouton_telecharger' in request.form:
            return generate_pdf_tous_logements(proprio,logements)
    return render_template("accueil_2.html", infos=infos[:4], justifies=a_justifier[:4])

@app.route("/accueil-admin/")
@login_required   
def accueil_admin():
    """
    Renvoie la page d'accueil d'un admin
    """
    avis = Avis.get_all()
    if avis != None:
        avis.reverse()
    user = User.get_all()
    if user != None:
        user.reverse()
    return render_template("accueil_admin.html", avis=avis[:2], user=user[:2])
    
@app.route("/information")
def information():
    """
    Renvoie la page 'information' du site
    """
    return render_template("information.html")

@app.route("/services")
def services():
    """
    Renvoie la page 'services' du site
    """
    return render_template("services.html")


@app.route("/mon-compte/", methods =("POST" ,"GET",))
def mon_compte():
    """
    Permet à l'utilisateur de modifier son profil
    """
    form = ModificationForm()
    if current_user.is_authenticated and current_user.proprio:
        form.nom.data = current_user.proprio.nom
        form.prenom.data = current_user.proprio.prenom
    if request.method == "POST":
        User.modifier(current_user.mail, request.form.get('nom'), request.form.get('prenom'))
        flash("Vos informations ont été mises à jour avec succès.", "success")
        return redirect(url_for('mon_compte'))
    return render_template("mon-compte.html", form=form)

@app.route("/ajout_avis/", methods=["POST"])
@login_required
def ajouter_avis():
    """Ajoute un avis à la base de données"""
    message = request.form.get('avis')
    proprio = current_user.proprio.id_proprio
    max_id = Avis.max_id()+1
    Avis.ajoute(Avis(max_id, message, proprio))
    return redirect(url_for('mon_compte'))

@app.route("/test/")
def test():
    return render_template_string(str(Logement.next_id()))

def extraire_informations(texte):
    """
    Fonction qui permet d'extraire le prix et la date d'achat d'un texte

    Args :
        texte (str) : le texte à analyser

    Return :
        un dictionnaire avec les clés "prix" et "date_achat", contenant les informations extraites
    """
    doc = nlp(texte)
    donnees = {"prix": "", "date_achat": ""}
    for ent in doc.ents:
        if ent.label_ == "PRIX":
            donnees["prix"] = ent.text
        elif ent.label_ == "DATE":
            donnees["date_achat"] = ent.text
    return donnees

    
@app.route("/open", methods=["GET"])
@login_required
def open_fic():
    url = request.args.get("url")
    return redirect(url_for('accueil_connexion'))
