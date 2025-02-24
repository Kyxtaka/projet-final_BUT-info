
from sqlalchemy.orm import registry, relationship, Session
from sqlalchemy import select, Column, Integer, String, Enum, Date, DECIMAL, Float, String, create_engine, DateTime, CheckConstraint
from ..constante import Base
from ...app import db
from sqlalchemy.sql.expression import func
from sqlalchemy.sql.schema import ForeignKey

class Categorie(Base):
    __tablename__ = "CATEGORIE"

    id_cat = Column(Integer,
                    primary_key=True,
                    nullable=False,
                    name="ID_CATEGORIE")
    nom_cat = Column(String(20), nullable=False, name="NOM_CATEGORIE")


    def __init__(self, id_cat, nom_cat):
        """init d'une catégorie de bien

        Args:
            id_cat (int): id de la catégorie (unique)
            nom_cat (str): nom de la catégorie
        """
        self.id_cat = id_cat
        self.nom_cat = nom_cat


    def __repr__(self):
        """représentation d'une catégorie de bien

        Returns:
            str: contenant l'id et le nom de la catégorie
        """
        return "<Categorie (%d) %s >" % (self.id_cat, self.nom_cat)


    def get_id_cat(self):
        """getter de l'id de la catégorie

        Returns:
            int: 
        """
        return self.id_cat


    def set_id_cat(self, id_cat):
        self.id_cat = id_cat


    def get_nom_cat(self):
        """getter du nom de la catégorie

        Returns:
            int: 
        """
        return self.nom_cat


    def set_nom_cat(self, nom_cat):
        """Modification du nom de la catégorie

        Args:
            nom_cat (str): nouveau nom de la catégorie
        """
        self.nom_cat = nom_cat
        
    @staticmethod
    def put_categorie(cat):
        db.session.add(cat)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        