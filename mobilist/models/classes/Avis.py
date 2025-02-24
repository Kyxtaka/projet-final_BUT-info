from sqlalchemy.orm import registry, relationship, Session
from sqlalchemy import select, Column, Integer, String, Enum, Date, DECIMAL, Float, String, create_engine, DateTime, CheckConstraint
from ..constante import Base
from ...app import db
from sqlalchemy.sql.expression import func
from sqlalchemy.sql.schema import ForeignKey

class Avis(Base):
    __tablename__ = "AVIS"


    id_avis = Column(Integer, name="ID_AVIS", primary_key=True)
    desc_avis = Column(String(1000), name="DESCRIPTION", nullable=True)
    id_proprio = Column(Integer, ForeignKey("PROPRIETAIRE.ID_PROPRIO", ondelete="CASCADE"), nullable=False, name="ID_PROPRIO")
    

    def __init__(self, id_avis, desc_avis, id_proprio):
        """Init d'un Avis

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
        self.id_avis = id_avis


    def get_desc_avis(self):
        """Getter de du contenu de l'avis

        Returns:
            str: Contenu de l'avis
        """
        return self.desc_avis


    def set_desc_avis(self, desc_avis):
        """Changer le contenu de l'avis

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
        self.id_proprio = id_proprio


    def get_sample():
        return Avis.query.all()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
