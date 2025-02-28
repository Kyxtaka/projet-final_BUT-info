from flask_wtf import FlaskForm
from wtforms import PasswordField

class ResetPasswordForm(FlaskForm):
    """
    Formulaire de réinitialisation du mot de passe

    Attributes :
        mdp (PasswordField) : Champ pour le nouveau mot de passe
        valider (PasswordField) : Champ de confirmation pour le nouveau mot de passe
    """
    mdp = PasswordField("Mot de passe")
    valider = PasswordField("Confirmer mot de passe")