from flask import flash

from mobilist.models.models import ChangePasswordToken
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
from ..login.classes.ResetPasswordForm import ResetPasswordForm
from mobilist.commands import create_user
from mobilist.secure_constante import PASSWD, GOOGLE_SMTP, GOOGLE_PORT, GOOGLE_SMTP_USER, GOOGLE_SMTP_PWD
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
            
            # verifie si le mail est déjà utilisé
            user_existant = User.query.filter_by(mail=form_inscription.mail.data).first()
            if user_existant:
                login_user(user_existant)
                flash("Ce compte existe déjà.", "error")
                return redirect(url_for('utilisateurs.lesUtilisateurs'))
            
            
            tentative = False
            genrated_token = ChangePasswordToken(accountEmail=form_inscription.mail.data) # generation du token avec validite de 10min par default
            try: 
                db.session.add(genrated_token)
                db.session.commit()
                tentative = True
                status = pwd_email(form_inscription.mail.data, genrated_token.get_token())
            except Exception as e:
                print("Erreur lors de la sauvegarde du token")
                print(e)
                tentative = True
            if tentative is None:
                flash("Mail non envoyé", "error")
                return render_template("lesUtilisateurs.html", tentative=False, form=form)
            elif not tentative:
                flash("Mail non envoyé", "error")
                return render_template("lesUtilisateurs.html", tentative=True, form=form)
            else:
                flash("Mail envoyé avec succès!", "success")
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


def pwd_email(mail, token) -> bool:
    """
    Fonction qui envoie un email d'inscription du mot de passe

    Args : 
        mail (str) : l'adresse mail
        token (str) : le token pour valider la demande de réinitialisation

    Returns : 
        bool : True si l'email a été envoyé avec succès, False si non
    """
    if not isinstance(mail, str) or "@" not in mail:
        print("Adresse email invalide :", mail)
        return False

    sent_status = False
    email = GOOGLE_SMTP_USER
    password = GOOGLE_SMTP_PWD
    subject = "Mobilist - Validez votre mot de passe"
    generated_change_password_link = f"http://127.0.0.1:5000/forgotPassword/setPassword?token={token}"

    body = f"""
    Pour vous inscrire chez Mobilist, veuillez valider votre mot de passe.
    Cliquez sur le lien suivant : {generated_change_password_link}
    Ce lien est valable 10 minutes.
    """

    try:
        print(f"Connexion SMTP à {GOOGLE_SMTP}:{GOOGLE_PORT}")
        server = smtplib.SMTP(GOOGLE_SMTP, GOOGLE_PORT)
        server.starttls()
        server.login(email, password)
        print("Authentification SMTP réussie")

        # Création de l'email
        msg = MIMEMultipart()
        msg["From"] = email
        msg["To"] = mail
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Envoi du mail
        server.sendmail(email, mail, msg.as_string())
        print("Email envoyé avec succès !")
        sent_status = True

    except smtplib.SMTPAuthenticationError:
        print("Erreur d'authentification SMTP. Vérifie ton email/mot de passe.")
    except smtplib.SMTPException as e:
        print(f"Erreur SMTP : {e}")
    except Exception as e:
        print(f"Erreur inconnue : {e}")
    finally:
        server.quit()

    return sent_status


@utilisateur_bp.route("/set_mdp/", methods=("GET", "POST",))
def set_mdp():
    valid_access = False
    token = request.args.get("token")
    if token:
        tokenObject = ChangePasswordToken.get_by_token(token)
        if tokenObject and not tokenObject.is_expired():  
            valid_access = True

    if not valid_access:  
        return render_template("unauthorized_access.html"), 401

    form_mdp = ResetPasswordForm()

    if form_mdp.is_submitted() and form_mdp.validate_on_submit():
        if form_mdp.mdp.data == form_mdp.valider.data:
            # Créer le propriétaire et l'utilisateur
            proprio = Proprietaire(nom=form_mdp.nom.data, prenom=form_mdp.prenom.data, mail=tokenObject.mail)
            db.session.add(proprio)
            db.session.commit()

            create_user(tokenObject.mail, form_mdp.mdp.data, "proprio")

            # Marquer le token comme utilisé
            tokenObject.set_used()
            db.session.commit()

            flash("Compte créé avec succès ! Vous pouvez maintenant vous connecter.", "success")
            return redirect(url_for('home'))

    return render_template("reinitialiser_mdp.html", form=form_mdp, token_access=token)
