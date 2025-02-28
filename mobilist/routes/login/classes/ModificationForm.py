from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, HiddenField
from wtforms.validators import DataRequired


class ModificationForm(FlaskForm):
    """
    Formulaire de modification du mot de passe

    Attributes :
        nom (StringField) : Champ pour le nom de l'utilisateur
        prenom (StringField) : Champ pour le prénom de l'utilisateur
        mdp_actuel (PasswordField) : Champ pour le mot de passe actuel de l'utilisateur
        mdp (PasswordField) : Champ pour le nouveau mot de passe
        mdp_confirm (PasswordField) : Champ de confirmation pour le nouveau mot de passe
    """
    nom = StringField('Votre Nom', validators=[DataRequired()])
    prenom = StringField('Votre Prénom', validators=[DataRequired()])
    mdp_actuel = PasswordField('Mot de passe actuel', validators=[DataRequired()])
    mdp = PasswordField('Nouveau mot de passe', validators=[DataRequired()])
    mdp_confirm = PasswordField('Confirmer le mot de passe', validators=[DataRequired()])
    different = False
