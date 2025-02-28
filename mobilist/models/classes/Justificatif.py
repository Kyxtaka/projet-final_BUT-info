

from sqlalchemy.orm import registry, relationship, Session
from sqlalchemy import select, Column, Integer, String, Enum, Date, DECIMAL, Float, String, create_engine, DateTime, CheckConstraint
from ..constante import Base
from ...app import db
from sqlalchemy.sql.expression import func
from sqlalchemy.sql.schema import ForeignKey

class Justificatif(Base):
    __tablename__ = "JUSTIFICATIF"


    id_justif = Column(Integer, primary_key=True, name="ID_JUSTIFICATIF")
    nom_justif = Column(String(30), name="NOM_JUSTIFICATIF")
    date_ajout = Column(Date, name="DATE_AJOUT")
    URL = Column(String(200), name="URL")
    id_bien = Column(Integer, ForeignKey("BIEN.ID_BIEN", ondelete="CASCADE"), primary_key=True, name="ID_BIEN")
    
    def __init__(self, id_justif, nom_justif, date_ajout, URL, id_bien):
        """Initialisation d'un justificatif

        Args:
            id_justif (int): ID du justificatif (unique)
            nom_justif (str): nom du justificatif
            date_ajout (str): date d'ajout
            URL (str): URL vers l'image du justificatif
            id_bien (int): ID du bien associé au justificatif
        """
        self.id_justif = id_justif
        self.nom_justif = nom_justif
        self.date_ajout = date_ajout
        self.URL = URL
        self.id_bien = id_bien


    def __repr__(self):
        """représentation du justificatif

        Returns:
            str: String contenant l'ID du justificatif, son nom, sa date d'ajout, et le lien vers l'image justificatif, ainsi que l'ID du bien associé
        """
        return "<Justificatif (%d) %s %s %s %d>" % (
            self.id_justif, self.nom_justif, self.date_ajout, self.URL,
            self.id_bien)

    def get_id_justif(self):
        """getter de l'ID du justificatif

        Returns:
            int: ID du justificatif
        """
        return self.id_justif


    def set_id_justif(self, id_justif):
        """setter de l'ID du justificatif
        
        Args:
            id_justif (int): le nouvel ID
        """
        self.id_justif = id_justif


    def get_nom_justif(self):
        """getter du nom du justificatif

        Returns:
            str: nom du justificatif
        """
        return self.nom_justif


    def set_nom_justif(self, nom_justif):
        """Modifie le nom du justificatif

        Args:
            nom_justif (str): nouveau nom du justificatif
        """
        self.nom_justif = nom_justif


    def get_date_ajout(self):
        """getter de la date d'ajout

        Returns:
            str: date de l'ajout du justificatif
        """
        return self.date_ajout


    def set_date_ajout(self, date_ajout):
        """setter de la date d'ajout

        Args:
            date_ajout (str): nouvelle date d'ajout
        """
        self.date_ajout = date_ajout


    def get_URL(self):
        """getter de l'URL vers l'image du justificatif

        Returns:
            str: URL vers l'image du justificatif
        """
        return self.URL


    def set_URL(self, URL):
        """setter de l'URL vers l'ilage du justificatif

        Args:
            URL (str): nouvel URL
        """
        self.URL = URL


    def get_id_bien(self):
        """getter de l'ID du bien associé

        Returns:
            int: ID du bien associé
        """
        return self.id_bien


    def set_id_bien(self, id_bien):
        """setter de l'ID du bien associé
        
        Args:
            id_bien(int): le nouvel ID
        """
        self.id_bien = id_bien
    
    @staticmethod
    def possede_justificatif(biens):
        """Vérifie si des biens possèdent un justificatif associé

        Args:
            biens (list): liste des biens à vérifier

        Returns:
            list: liste des biens qui ne possèdent pas de justificatif associé
        """
        liste_non_justifies = []
        for bien in biens:
            for j in range(len(bien)):
                result = Justificatif.query.filter_by(id_bien=bien[j].id_bien).first()
                if result==None:
                    liste_non_justifies.append(bien[j])
        return liste_non_justifies
                    

    @staticmethod
    def get_max_id():
        """Retourne l'ID maximal des justificatifs présents dans la base de données

        Returns:
            int: Le plus grand ID de justificatif, si il n'y en a pas retourne 'None'
        """
        return db.session.query(func.max(Justificatif.id_justif)).scalar()
    
    @staticmethod
    def next_id():
        """Retourne l'ID suivant pour un nouveau justificatif

        Returns:
            int: L'ID suivant pour un nouveau justificatif
        """
        if Justificatif.get_max_id() is None:
            return 1
        return Justificatif.get_max_id() + 1
    
    @staticmethod
    def put_justificatif(justif):
        """Ajoute un justificatif dans la base de données

        Args:
            justif (Justificatif): le justificatif à ajouter dans la base de données
        """
        db.session.add(justif)
        db.session.commit()
