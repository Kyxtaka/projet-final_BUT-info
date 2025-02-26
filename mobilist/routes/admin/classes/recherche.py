from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class RechercheForm(FlaskForm):
    champ = StringField(validators=[DataRequired()])
    rechercher = SubmitField()