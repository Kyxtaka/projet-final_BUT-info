from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, HiddenField
from wtforms.validators import DataRequired, Email
from hashlib import sha256
from mobilist.models.models import User 

class InscriptionForm(FlaskForm):
    """
    Formulaire d'inscription pour un utilisateur

    Attributes :
        nom (StringField) : Champ pour le nom
        prenom (StringField) : Champ pour le prénom
        mail (StringField) : Champ pour l'adresse e-mail
        password (PasswordField) : Champ pour le mot de passe
        next (HiddenField) : Champ caché pour la page vers laquelle rediriger après l'inscription

    Methods :
        get_authenticated_user() : Vérifie si l'utilisateur existe déjà dans la base de données
        Renvoie l'utilisateur s'il existe, sinon None
    """
    nom = StringField('Nom', validators=[DataRequired(message="Le nom est requis")])
    prenom = StringField('Prénom', validators=[DataRequired(message="Le prénom est requis")])
    mail = StringField('Adresse e-mail', validators=[DataRequired(message="L'email est requis")])
    password = PasswordField('Mot de passe', validators=[DataRequired(message="Le mot de passe est requis")])
    next = HiddenField()

    def get_authenticated_user(self):
        """
        Recherche l'utilisateur dans la base de données à partir de son adresse e-mail

        Returns : 
            user (User) ou None : l'utilisateur authentifié si le mot de passe est correct, sinon None
       """
        user = User.query.get(self.mail.data)
        if user is None:
            return None
        m = sha256()
        m.update(self.password.data.encode())
        passwd = m.hexdigest()
        return user if passwd == user.password else None
