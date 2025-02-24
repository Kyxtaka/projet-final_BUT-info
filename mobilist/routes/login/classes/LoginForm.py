
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, HiddenField
from hashlib import sha256
from mobilist.models.models import User 

class LoginForm(FlaskForm):
    """
    Formulaire de connexion pour un utilisateur 

    Attributes :
        mail (StringField) : Champ pour l'adresse e-mail 
        password (PasswordField) : Champ pour le mot de passe
        next (HiddenField) : Champ caché pour la page vers laquelle rediriger après la connexion
        id (HiddenField) : Champ caché pour l'identifiant de l'utilisateur 

    Methods :
        get_authenticated_user() : Vérifie l'authenticité de l'utilisateur
        Renvoie l'utilisateur authentifié si les informations sont valides, sinon None
    """
    mail = StringField('Adresse e-mail')
    password = PasswordField('Mot de passe')
    next = HiddenField()
    id = HiddenField()

    def get_authenticated_user(self):
        """
        Recherche l'utilisateur dans la base de données à partir de son adresse e-mail, et hache le mots de passe

        Returns : 
            user (User) ou None: l'utilisateur authentifié si le mot de passe est correct, sinon None
        """
        user = User.query.get(self.mail.data)
        if user is None:
            return None
        m = sha256()
        m.update(self.password.data.encode())
        passwd = m.hexdigest()
        return user if passwd == user.password else None