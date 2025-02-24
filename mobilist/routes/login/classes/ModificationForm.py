from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, HiddenField
from wtforms.validators import DataRequired


class ModificationForm(FlaskForm):
    nom = StringField('Votre Nom', validators=[DataRequired()])
    prenom = StringField('Votre Prénom', validators=[DataRequired()])
    mdp_actuel = PasswordField('Mot de passe actuel',
                               validators=[DataRequired()])
    mdp = PasswordField('Nouveau mot de passe', validators=[DataRequired()])
    mdp_confirm = PasswordField('Confirmer le mot de passe', validators=[DataRequired()])
    different = False
