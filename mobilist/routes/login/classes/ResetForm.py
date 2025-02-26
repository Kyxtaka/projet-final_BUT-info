
from flask_wtf import FlaskForm
from wtforms import StringField

class ResetForm(FlaskForm):
    """
    Formulaire de réinitialisation du mot de passe, demande une adresse e-mail pour envoyer un lien de réinitialisation

    Attributes :
        email (StringField) : Champ pour saisir l'adresse e-mail
    """
    email = StringField("Votre email")