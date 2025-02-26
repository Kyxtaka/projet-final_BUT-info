
from sqlalchemy.orm import registry, relationship, Session
from sqlalchemy import select, Column, Integer, String, Enum, Date, DECIMAL, Float, String, create_engine, DateTime, CheckConstraint
from ..constante import Base
from ...app import db
from sqlalchemy.sql.expression import func
from sqlalchemy.sql.schema import ForeignKey

class TypeBien(Base):
    __tablename__ = "TYPEBIEN"

    id_type = Column(Integer,
                     primary_key=True,
                     nullable=False,
                     name="ID_TYPE_BIEN")
    nom_type = Column(String(20), nullable=False, name="NOM_TYPE")


    def __init__(self, id_type, nom_type):
        """Initialisation d'un type de bien

        Args:
            id_type (int): id du type de bien
            nom_type (str): nom du type de bien
        """
        self.id_type = id_type
        self.nom_type = nom_type


    def __repr__(self):
        """représentation du type de bien

        Returns:
            str: contenant l'id et le nom du type
        """
        return "<TypeBien (%d) %s >" % (self.id_type, self.nom_type)


    def get_id_type(self):
        """getter de l'id du type

        Returns:
            int: l'id du type
        """
        return self.id_type


    def set_id_type(self, id_type):
        self.id_type = id_type


    def get_nom_type(self):
        """getter du nom du type 

        Returns:
            str: nom du type de bien
        """
        return self.nom_type


    def set_nom_type(self, nom_type):
        """changer le nom du type

        Args:
            nom_type (str): nouveau nom du type de bien
        """
        self.nom_type = nom_type
        
    @staticmethod
    def put_type(type):
        """Ajoute un nouveau type de bien à la base de données

        Args:
            type (TypeBien): le type à ajouter
        """
        db.session.add(type)
        db.session.commit()

    def delete(self):
        """Supprime un type de bien de la base de données
        """
        db.session.delete(self)
        db.session.commit()