
from sqlalchemy.orm import registry, relationship, Session
from sqlalchemy import select, Column, Integer, String, Enum, Date, DECIMAL, Float, String, create_engine, DateTime, CheckConstraint
from ..constante import Base
from sqlalchemy.sql.expression import func
from ...app import db
from sqlalchemy.sql.schema import ForeignKey
from .Logement import AVOIR
from .User import User
from .Justificatif import Justificatif

class Proprietaire(Base):
    __tablename__ = "PROPRIETAIRE"

    id_proprio = Column(Integer, primary_key=True, name="ID_PROPRIO")
    nom = Column(String(20), name="NOM")
    prenom = Column(String(20), name="PRENOM")
    mail = Column(String(50), name="MAIL", unique=True, nullable=False)
    logements = relationship("Logement", secondary="AVOIR", back_populates="proprietaires", cascade="all, delete")
    user = relationship("User", back_populates="proprio", cascade="all, delete", uselist=False)
    
    def __init__(self, id_proprio, mail , nom_proprio=None, prenom_proprio=None):
        self.id_proprio = id_proprio
        self.mail = mail
        self.nom = nom_proprio
        self.prenom = prenom_proprio
    
    
    def __repr__(self):
        """Représentation d'un propriétaire

        Returns:
            str: Une chaîne de caractère contenant l'ID, le nom, et le prénom
        """
        return "<Proprietaire (%d) %s %s>" % (self.id_proprio, self.nom,
                                              self.prenom)

    def get_id_proprio(self):
        """Getter de l'ID du propriétaire

        Returns:
            int: ID du propriétaire
        """
        return self.id_proprio


    def set_id_proprio(self, id_proprio):
        self.id_proprio = id_proprio


    def get_nom(self):
        """Getter du nom

        Returns:
            str: Nom du propriétaire
        """
        return self.nom


    def set_nom(self, nom):
        """Changer le nom 

        Args:
            nom (str): Nouveau nom
        """
        self.nom = nom


    def get_prenom(self):
        """Getter du prénom 

        Returns:
            str: Prénom du propriétaire
        """
        return self.prenom
    
    def get_mail(self):
        """Getter du mail  

        Returns:
            str: mail du propriétaire
        """
        return self.mail

    def set_prenom(self, prenom):
        self.prenom = prenom


    @staticmethod
    def max_id():
        max_id =  db.session.query(func.max(Proprietaire.id_proprio)).scalar()
        return max_id


    @staticmethod
    def get_by_mail(mail):
        return Proprietaire.query.filter_by(mail=mail).first()
    
    def delete(self):
        for logement in self.logements:
            logement.delete()
        AVOIR.get_biens_by_id(self.id_logement).delete()
        User.query.filter_by(mail=self.mail).delete()
        db.session.delete(self)
        db.session.commit()
        
    @staticmethod
    def put_proprio(proprio):
       db.session.add(proprio)
       db.session.commit()
   