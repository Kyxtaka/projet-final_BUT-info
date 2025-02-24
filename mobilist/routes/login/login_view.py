# Importations de modules 
from mobilist.secure_constante import GOOGLE_SMTP, GOOGLE_SMTP_PWD, GOOGLE_SMTP_USER
from mobilist.models import *
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

from flask import (flash, render_template, redirect, render_template, url_for)

from flask import Blueprint


# Route pour la page de réinitialisation du mot de passe
bp = Blueprint('login', __name__)
@bp.route("/forgotPassword/setPassword", methods=["POST", "GET"])
def set_password_page():
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

        # Envoie l'email
        server.sendmail(email, mail, msg.as_string())
        print("Email envoyé avec succès !")
        sent_status = True
    except Exception as e:
        print(f"Une erreur est survenue : {e}")
        sent_status = False
    finally:
        server.quit()
        return sent_statusResetPasswordForm

@bp.route("/forgotPassword/", methods=["POST", "GET"])
def page_oublie():
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
def modif_mdp():
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

def hash_password(password):
    m = sha256()
    m.update(password.encode())
    return m.hexdigest()


@bp.route("/login/", methods =("GET","POST" ,))
def login() -> str:
    f = LoginForm()
    if not f.is_submitted():
        f.next.data = request.args.get("next")
    elif f.validate_on_submit():
        user = f.get_authenticated_user()
        if user:
            login_user(user)
            next = f.next.data or url_for("accueil_connexion")
            return redirect(next)
        return render_template(
        "connexion.html",
        form=f,mdp=False)
    return render_template(
    "connexion.html",
    form=f,mdp=True)

from flask_login import logout_user
@bp.route("/logout/")
def logout():
    logout_user()
    return redirect(url_for('home'))


@bp.route("/inscription/", methods=("GET", "POST",))
def inscription():
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
        return redirect(url_for("accueil_connexion"))
    return render_template(
    "inscription.html", form=f, present=False)

