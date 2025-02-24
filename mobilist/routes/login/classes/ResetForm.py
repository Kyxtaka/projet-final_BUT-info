
from flask_wtf import FlaskForm
from wtforms import StringField

class ResetForm(FlaskForm):
    email = StringField("Votre email")