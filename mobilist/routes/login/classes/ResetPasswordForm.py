from flask_wtf import FlaskForm
from wtforms import PasswordField

class ResetPasswordForm(FlaskForm):
    mdp = PasswordField("Mot de passe")
    valider = PasswordField("Confirmer mot de passe")