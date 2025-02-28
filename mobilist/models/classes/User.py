
from sqlalchemy.orm import registry, relationship, Session
from sqlalchemy import select, Column, Integer, String, Enum, Date, DECIMAL, Float, String, create_engine, DateTime, CheckConstraint
from ..constante import Base
from ...app import db
from flask_login import UserMixin
from sqlalchemy.sql.expression import func
from sqlalchemy.sql.schema import ForeignKey
from hashlib import sha256



class User(Base, UserMixin):
    __tablename__ = "USER"


    mail = Column(String(50), primary_key=True, name="MAIL")
    password = Column(String(64), name="PASSWORD")
    role = Column(String(10), name="ROLE")
    id_user = Column(Integer, ForeignKey("PROPRIETAIRE.ID_PROPRIO", ondelete="CASCADE"), name="ID_PROPRIO")    
    proprio = relationship('Proprietaire', back_populates='user', uselist=False, cascade="all, delete")
    
    def __init__(self, mail, password, role, id_user):
        self.mail = mail
        self.password = password
        self.role = role
        self.id_user = id_user
                
    def get_id(self):
        """getter du mail (id)

        Returns:
            str:  mail du user
        """
        return self.mail
    
    def set_id(self, mail):
        """setter du mail

        Args:
            mail (str): nouveau mail du user
        """
        self.mail = mail


    def get_password(self):
        """getter du mot de passe de user

        Returns:
            str: mot de passe de user
        """
        return self.password


    def set_password(self, password):
        """modifie le mot de passe de user

        Args:
            password (str): nouveau mot de passe
        """
        m = sha256()
        m.update(password.encode())
        self.password = m.hexdigest()    
    
    def get_role(self):
        """getter du role de user

        Returns:
            str: role de user
        """
        return self.role


    def set_role(self, role):
        """modifie le role de user

        Args:
            role (str): nouveau role de user
        """
        self.role = role


    def get_id_user(self):
        """getter de l'id de user

        Returns:
            int: id de user
        """
        return self.id_user


    def set_id_user(self, id_user):
        """setter de l'id de user

        Args:
            id_user (int): id de user
        """
        self.id_user = id_user

    @staticmethod
    def modifier(email, nom, prenom):
        """Modifie les informations du propriétaire associé à un user

        Args:
            email (str): l'email de l'utilisateur
            nom (str): le nouveau nom
            prenom (str): le nouveau prénom
        """
        proprio = db.session.get(User, email)
        try:
            proprio.proprio.set_nom(nom)
            proprio.proprio.set_prenom(prenom)
            db.session.commit()
        except: 
            print("L'utilisateur n'existe pas")

    @staticmethod
    def get_user(mail):
        """Retourne un utilisateur par son email

        Args:
            mail (str): l'email de l'utilisateur

        Returns:
            User: le user correspondant à l'email fourni
        """
        return User.query.get_or_404(mail)
    
    @staticmethod
    def get_by_mail(mail):
        """Retourne un utilisateur par son email

        Args:
            mail (str): l'email de l'utilisateur

        Returns:
            User: le user correspondant à l'email, ou 'None'
        """
        return User.query.filter_by(mail=mail).first()
    
    
    @staticmethod
    def put_user(user):
        """Ajoute un nouvel utilisateur à la base de données

        Args:
            user (User): le user à ajouter
        """
        db.session.add(user)
        db.session.commit()
    
    @staticmethod
    def get_all():
        """Retourne tous les utilisateurs

        Returns:
            list: la liste des users correspondant à tous les utilisateurs
        """
        return User.query.all()
    
    def set_proprio(self, proprio):
        """Associe un propriétaire à un utilisateur

        Args:
            proprio (Proprietaire): le propriétaire à associer à l'utilisateur
        """
        self.proprio = proprio
        

