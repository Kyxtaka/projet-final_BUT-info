from sqlalchemy import Column, Integer, String, DateTime, CheckConstraint
from ..app import db, login_manager
from sqlalchemy.sql.schema import ForeignKey
from datetime import datetime, timedelta
from sqlalchemy.sql.expression import func
import os.path
from .constante import Base
from .classes.User import User


def set_base(db):
    global Base
    Base=db.Model

class ChangePasswordToken(Base):
    """
    Classe pour un token de changement de mot de passe

    Attributes:
        accountEmail (str): l'email du compte utilisateur lié au token
        token (str): le token de changement de mot de passe
        datetime (datetime): la date et l'heure de la création du token
        duration (int): la durée de validité du token (en minutes)
        expiration (datetime): la date et l'heure d'expiration du token
        used (int): un indicateur pour savoir si le token a été utilisé (0 si non utilisé, 1 si utilisé)
    """
    __tablename__ = "CHANGEPASSWORDTOKEN"
    accountEmail = Column(String(50), ForeignKey("USER.MAIL"), primary_key=True, name="ACCOUNT_EMAIL")
    token = Column(String(64), name="TOKEN")
    datetime = Column(DateTime, name="DATETIME")
    duration = Column(Integer, name="DURATION")
    expiration = Column(DateTime, name="EXPIRATION")
    used = Column(Integer, CheckConstraint('USED IN (0, 1)'), name="USED")

    def __init__(self, accountEmail, duration=10):
        """
        Initialise un token, si un token existe déjà pour cet utilisateur, il est supprimé et un nouveau est créé

        Args:
            accountEmail (str): l'email du compte utilisateur
            duration (int): la durée de validité du token (en minutes)
        """
        if ChangePasswordToken.query.filter_by(accountEmail=accountEmail).first():
            db.session.delete(ChangePasswordToken.query.filter_by(accountEmail=accountEmail).first())
            db.session.commit()
        self.accountEmail = accountEmail
        self.token = os.urandom(32).hex()
        self.datetime = datetime.now()
        self.duration = duration
        self.expiration = self.datetime + timedelta(minutes=duration)
        self.used = 0

    def is_expired(self) -> bool:
        """
        Vérifie si le token a expiré ou s'il a été utilisé

        Returns:
            bool: True si le token est expiré ou déjà utilisé, sinon False
        """
        return datetime.now() > self.expiration or self.used == 1
    
    def liked_user(self) -> User:
        """
        Retourne l'utilisateur lié au token

        Returns:
            User: l'utilisateur
        """
        return User.query.get(self.accountEmail)
    
    def get_token(self) -> str:
        """
        Retourne le token de changement de mot de passe

        Returns:
            str: le token
        """
        return self.token
    
    def get_email(self) -> str:
        """
        Retourne l'email associé au token

        Returns:
            str: l'email du compte utilisateur lié au token
        """
        return self.accountEmail
    
    def set_used(self) -> None:
        """
        Indique le token comme utilisé et l'enregistre dans la base de données
        """
        self.used = 1
        db.session.commit()
    
    @staticmethod
    def verify_token(token: str) -> bool:
        """
        Vérifie si un token donné existe dans la base de données

        Args:
            token (str): le token à vérifier

        Returns:
            bool: True si le token existe, sinon False
        """
        return ChangePasswordToken.query.filter_by(token=token).first() is not None
    
    @staticmethod
    def get_by_token(token: str) -> 'ChangePasswordToken':
        """
        Récupère le token correspondant à un token donné

        Args:
            token (str): le token à rechercher

        Returns:
            ChangePasswordToken: l'objet ChangePasswordToken correspondant au token, ou None si non trouvé
        """
        return ChangePasswordToken.query.filter_by(token=token).first()
    
    @staticmethod
    def delete_by_token(token: str) -> bool:
        """
        Supprime un token de changement de mot de passe à partir de son token

        Args:
            token (str): le token à supprimer

        Returns:
            bool: True si la suppression a réussi, sinon False
        """
        try:
            db.session.delete(ChangePasswordToken.query.filter_by(token=token).first())
            db.session.commit()
            return True
        except:
            db.session.rollback()
            return False

@login_manager.user_loader
def load_user(mail):
    """
    Charge l'utilisateur à partir de son email

    Args:
        mail (str): l'email de l'utilisateur

    Returns:
        User: l'utilisateur correspondant à l'email, ou None si l'utilisateur n'existe pas
    """
    return db.session.get(User, mail)

def get_next_id(table: object) -> int:
    """
    Récupère le prochain ID disponible pour une table donnée

    Args:
        table (object): la table

    Returns:
        int: le prochain ID disponible pour la table
    """
    return db.session.query(func.max(table)).scalar() + 1