# Importations de modules 
from mobilist.secure_constante import GOOGLE_SMTP, GOOGLE_SMTP_PWD, GOOGLE_SMTP_USER
from mobilist.models.models import *
from mobilist.exception import *
from mobilist.commands import create_user
from .classes.LoginForm import LoginForm
from .classes.InscriptionForm import InscriptionForm
from .classes.ModificationForm import ModificationForm
from .classes.ResetForm import ResetForm
from .classes.ResetPasswordForm import ResetPasswordForm
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from hashlib import sha256
from flask_login import login_user , current_user
from flask import request
from mobilist.exception import * 
from flask_login import logout_user


from flask import (flash, render_template, redirect, render_template, url_for)

from flask import Blueprint
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


bp = Blueprint('login', __name__)


@bp.route("/forgotPassword/setPassword", methods=["POST", "GET"])
def set_password_page() -> str:
    """
    Fonction qui permet à l'utilisateur de mettre à jour son mots de passe

    Returns:
        str:
            - Si le token est invalide ou expiré, renvoie la page d'accès non autorisé (401)
            - Si le token est valide et le formulaire soumis avec succès, redirige vers la page d'accueil
            - Sinon affiche la page de réinitialisation du mot de passe
    """
    valid_access = False
    if request.args.get("token"):
        token = request.args.get("token")  # Vérifie si un token est présent dans l'URL
        tokenObject = ChangePasswordToken.get_by_token(token)
        if tokenObject is None:  # Si le token est invalide
            valid_access = False
        else:
            valid_access = not tokenObject.is_expired() # Vérifie si le token est expiré
            print(f"token: {token}")
            print(f"is expired: {tokenObject.is_expired()}")
            print(f"valid_access: {valid_access}")
    if not valid_access:  # Si le token est invalide ou expiré
        return render_template(f"unauthorized_access.html"), 401
    # Si l'accès est valide, création du formulaire
    user = User.get_by_mail(ChangePasswordToken.get_by_token(token).get_email())
    form = ResetPasswordForm()
    if form.is_submitted():
        if form.mdp.data == form.valider.data:
            user.set_password(form.mdp.data)
            tokenObject.set_used()
            db.session.commit()
            return redirect(url_for('home'))
    return render_template("reinitialiser_mdp.html", form=form, tentative=False, token_access=tokenObject.get_token())

def send_change_pwd_email(mail, token) -> bool:
    """
    Fonction qui envoie un email de réinitialisation du mot de passe

    Args : 
        mail (str) : l'adresse mail
        token (str) : le token pour valider la demande de réinitialisation

    Returns : 
        bool : True si l'email a été envoyé avec succès, False si non
    """
    sent_status = False
    email = GOOGLE_SMTP_USER
    password = GOOGLE_SMTP_PWD
    subject = "Mobilist - réinitialiser votre mot de passe"
    protocol = "http"
    domain = "127.0.0.1"
    port = "5000"
    generated_change_password_link = f"{protocol}://{domain}:{port}/forgotPassword/setPassword?token={token}"
    body = f"""
    Pour réinitialiser votre mot de passe Mobilist,
    veuillez accéder à la page suivante : {generated_change_password_link}
    Ce lien est à usage unique et expirera dans 10 minutes.
    """
    try:
        # Configuration du serveur SMTP
        server = smtplib.SMTP(GOOGLE_SMTP)
        server.starttls() 
        server.login(email, password)

        # Création de l'email
        msg = MIMEMultipart()
        msg["From"] = email
        msg["To"] = mail
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Envoie de l'email
        server.sendmail(email, mail, msg.as_string())
        print("Email envoyé avec succès !")
        sent_status = True
    except Exception as e:
        print(f"Une erreur est survenue : {e}")
        sent_status = False
    finally:
        server.quit()
        return sent_status


@bp.route("/forgotPassword/", methods=["POST", "GET"])
def page_oublie() -> str:
    """
    Fonction qui permet d'envoyer un lien de réinitialisation de mot de passe

    Returns:
        str:
            - Si le formulaire n'a pas encore été soumis, affiche la page pour demander la réinitialisation du mot de passe
            - Si un e-mail a été soumis, affiche une page de confirmation d'envoi du lien de réinitialisation ou une page d'erreur
    """
    form = ResetForm()
    tentative = None
    if form.is_submitted():
        tentative = False
        user = User.get_by_mail(form.email.data)
        if user != None:
            genrated_token = ChangePasswordToken(user.get_id()) # generation du token avec validite de 10min par default
            try: 
                db.session.add(genrated_token)
                db.session.commit()
                tentative = True
                status = send_change_pwd_email(form.email.data, genrated_token.get_token())
            except Exception as e:
                print("Erreur lors de la sauvegarde du token")
                print(e)
                tentative = True
    if tentative is None:
        return render_template("mdp_oublie.html", tentative=False, form=form)
    elif not tentative:
        return render_template("mdp_oublie.html", tentative=True, form=form)
    else:
        return render_template("envoi_email.html", email=form.email.data)

@bp.route("/modif_mdp/", methods =("POST" ,"GET",))
def modif_mdp() -> str:
    """
    Fonction qui permet à l'utilisateur de modifier son mot de passe

    Returns:
        str: 
            - Si le formulaire est soumis et que le mot de passe est mis à jour, l'utilisateur est redirigé vers la page de son compte
            - Si une erreur se produit, la page de modification est renvoyée
    """
    form = ModificationForm()
    if request.method == "POST":
        print("submit")
        user = User.get_by_mail(current_user.mail)
        if hash_password(request.form.get('mdp_actuel')) == user.get_password():
            print("check passed")
            test = request.form.get('mdp')
            confirmation = request.form.get('mdp_confirm')
            if test == confirmation :
                print("same")
                user.set_password(test)
                db.session.commit()
                flash("Votre mot de passe a été mis à jour avec succès.", "success")
            else :
                form.different = True
        return redirect(url_for('mon_compte'))
    return render_template("mon-compte.html", form=form)

def hash_password(password) -> str:
    """
    Fonction qui prend un mot de passe en texte brut, et renvoit son hachage avec l'algorithme SHA-256

    Args:
        password (str) : le mot de passe à hacher

    Returns:
        str : le hachage du mot de passe sous forme de chaîne hexadécimale
    """
    m = sha256()
    m.update(password.encode())
    return m.hexdigest()


@bp.route("/login/", methods =("GET","POST" ,))
def login() -> str:
    """
    Fonction qui permet à un utilisateur de se connecter via un formulaire de connexion

    Returns:
        str:
            - Si l'utilisateur est authentifié avec succès, il est redirigé vers la page demandée
            - Si l'utilisateur échoue à s'authentifier, il reste sur la page de connexion avec un message d'erreur
    """
    f = LoginForm()
    if not f.is_submitted():
        f.next.data = request.args.get("next")
    elif f.validate_on_submit():
        user = f.get_authenticated_user()
        if user:
            if user.get_role() != 'admin':  
                login_user(user)
                next = f.next.data or url_for("accueil_connexion")
                return redirect(next)
            # si l'utilisateur est un admin :
            login_user(user) 
            next = f.next.data or url_for("accueil_admin")
            return redirect(next)
        return render_template(
        "connexion.html",
        form=f,mdp=False)
    return render_template(
    "connexion.html",
    form=f,mdp=True)

@bp.route("/logout/")
def logout():
    """
    Déconnecte l'utilisateur actuel et le redirige vers la page d'accueil
    """
    logout_user()
    return redirect(url_for('home'))


@bp.route("/inscription/", methods=("GET", "POST",))
def inscription():
    """
    Fonction qui permet à un utilisateur de s'inscrire via le formulaire d'inscription
   
    Returns:
        str: 
            - Si le formulaire est soumis et que l'inscription réussit, l'utilisateur est redirigé vers la page d'accueil connecté
            - Si l'utilisateur existe déjà, il reste sur la page d'inscription avec un message d'erreur
    """
    f = InscriptionForm()
    if not f.is_submitted():
        f.next.data = request.args.get("next")
    elif f.validate_on_submit():
        user = f.get_authenticated_user()
        if user:
            login_user(user)
            return render_template("inscription.html", form=f, present=True)
        create_user(f.mail.data, f.password.data, "proprio")
        User.modifier(f.mail.data, f.nom.data, f.prenom.data)
        return redirect(url_for("login.login"))
    return render_template(
    "inscription.html", form=f, present=False)

