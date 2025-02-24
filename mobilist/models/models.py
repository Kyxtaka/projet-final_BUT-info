from hashlib import sha256
from sqlalchemy.orm import registry, relationship, Session
from sqlalchemy import select, Column, Integer, String, Enum, Date, DECIMAL, Float, String, create_engine, DateTime, CheckConstraint
from ..app import db, login_manager
from sqlalchemy.sql.schema import ForeignKey
from datetime import date, datetime, timedelta
from flask_login import UserMixin
from sqlalchemy.sql.expression import func
from hashlib import sha256
from sqlalchemy import desc
import yaml, os.path
import time
from jinja2 import (
    Environment,
    FileSystemLoader,
)
from io import BytesIO
from .constante import Base
from .classes.User import User
from .classes.TypeBien import TypeBien
from .classes.Proprietaire import Proprietaire
from .classes.Logement import Piece
from .classes.Logement import LogementType
from .classes.Logement import Logement
from .classes.Justificatif import Justificatif
from .classes.Categorie import Categorie
from .classes.Logement import Bien
from .classes.Logement import AVOIR
from .classes.Avis import Avis


def set_base(db):
    global Base
    Base=db.Model

class ChangePasswordToken(Base):
    __tablename__ = "CHANGEPASSWORDTOKEN"
    accountEmail = Column(String(50), ForeignKey("USER.MAIL"), primary_key=True, name="ACCOUNT_EMAIL")
    token = Column(String(64), name="TOKEN")
    datetime = Column(DateTime, name="DATETIME")
    duration = Column(Integer, name="DURATION")
    expiration = Column(DateTime, name="EXPIRATION")
    used = Column(Integer, CheckConstraint('USED IN (0, 1)'), name="USED")

    def __init__(self, accountEmail, duration=10): # generation d'un token ==> supprime l'ancien ci une nouvelle requette est demander et que un token existe celui ci est automatiquement supprimer
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
        return datetime.now() > self.expiration or self.used == 1
    
    def liked_user(self) -> User:
        return User.query.get(self.accountEmail)
    
    def get_token(self) -> str:
        return self.token
    
    def get_email(self) -> str:
        return self.accountEmail
    
    def set_used(self) -> None:
        self.used = 1
        db.session.commit()
    
    @staticmethod
    def verify_token(token: str) -> bool:
        return ChangePasswordToken.query.filter_by(token=token).first() is not None
    
    @staticmethod
    def get_by_token(token: str) -> 'ChangePasswordToken':
        return ChangePasswordToken.query.filter_by(token=token).first()
    
    @staticmethod
    def delete_by_token(token: str) -> bool:
        try:
            db.session.delete(ChangePasswordToken.query.filter_by(token=token).first())
            db.session.commit()
            return True
        except:
            db.session.rollback()
            return False

@login_manager.user_loader
def load_user(mail):
    return db.session.get(User, mail)

def get_next_id(table: object) -> int:
    """_summary_

    Args:
        table (object): La table pour laquelle on veut obtenir le prochain ID

    Returns:
        int: Le prochain ID disponible pour la table
    """
    return db.session.query(func.max(table)).scalar() + 1