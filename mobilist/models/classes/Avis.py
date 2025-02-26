from sqlalchemy.orm import registry, relationship, Session
from sqlalchemy import select, Column, Integer, String, Enum, Date, DECIMAL, Float, String, create_engine, DateTime, CheckConstraint
from ..constante import Base
from ...app import db
from sqlalchemy.sql.expression import func
from sqlalchemy.sql.schema import ForeignKey
from .Proprietaire import Proprietaire

class Avis(Base):
    __tablename__ = "AVIS"


    id_avis = Column(Integer, name="ID_AVIS", primary_key=True)
    desc_avis = Column(String(1000), name="DESCRIPTION", nullable=True)
    id_proprio = Column(Integer, ForeignKey("PROPRIETAIRE.ID_PROPRIO", ondelete="CASCADE"), nullable=False, name="ID_PROPRIO")
    

    def __init__(self, id_avis, desc_avis, id_proprio):
        """Initialise un objet Avis

        Args:
            id_avis (int): ID unique de l'avis
            desc_avis (str): Contenu de l'avis (nullable)
            id_proprio (int): ID unique du propriétaire ayant posté l'avis
        """
        self.id_avis = id_avis
        self.desc_avis = desc_avis
        self.id_proprio = id_proprio


    def __repr__(self):
        """Représentation de la classe Avis

        Returns:
            str: Chaîne de caractère contenant l'id de l'avis et sa description
        """
        return "<Avis (%d) %s>" % (self.id_avis, self.desc_avis)


    def get_id_avis(self):
        """Getter de l'ID de l'avis

        Returns:
            int: ID de l'avis
        """
        return self.id_avis


    def set_id_avis(self, id_avis):
        """Setter de l'ID de l'avis

        Args : 
            id_avis (int) : nouvel id
        """
        self.id_avis = id_avis


    def get_desc_avis(self):
        """Getter du contenu de l'avis

        Returns:
            str: Contenu de l'avis
        """
        return self.desc_avis


    def set_desc_avis(self, desc_avis):
        """Setter du contenu de l'avis

        Args:
            desc_avis (str): Nouveau contenu pour l'avis
        """
        self.desc_avis = desc_avis


    def get_id_proprio(self):
        """Getter de l'ID du propriétaire (ayant posté l'avis)

        Returns:
            int: ID du propriétaire
        """
        return self.id_proprio


    def set_id_proprio(self, id_proprio):
        """Setter de l'ID d'un propriétaire

        Args:
            id_proprio (int) : le nouvel ID
        """
        self.id_proprio = id_proprio


    def get_sample():
        """Retourne tous les avis

        Returns:
            list: liste de tous les avis dans la base de données
        """
        return Avis.query.all()
    
    def delete(self):
        """Supprime l'avis de la session, dans la base de données
        """
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def max_id():
        """get max id categorie"""
        max_id = db.session.query(func.max(Avis.id_avis)).scalar()
        return max_id

    @staticmethod
    def get_all():
        """Getter de tous les categories

        Returns:
            list<Categorie>: tous les categories
        """
        return db.session.query(Avis, Proprietaire).join(Proprietaire).all()
        
