import enum
from sqlalchemy.orm import registry, relationship, Session
from sqlalchemy import select, Column, Integer, String, Enum, Date, DECIMAL, Float, String, create_engine, DateTime, CheckConstraint
from ..constante import Base
from ...app import db
from sqlalchemy.sql.expression import func
from sqlalchemy.sql.schema import ForeignKey
from .User import User
from sqlalchemy import desc
from .Justificatif import Justificatif
import json

class LogementType(enum.Enum):
    __tablename__ = "LOGEMENTTYPE"


    APPART = "appart"
    MAISON = "maison"

    def get_type(self):
        return self.name

    def get_type(self):
        return self.name

class Logement(Base):
    __tablename__ = "LOGEMENT"


    id_logement = Column(Integer, name="ID_LOGEMENT", primary_key=True)
    nom_logement = Column(String(20), name="NOM_LOGEMENT", nullable=True)
    type_logement = Column(Enum(LogementType),
                           name="TYPE_LOGEMENT",
                           nullable=False)
    adresse = Column(String(100), name="ADRESSE", nullable=True)
    desc_logement = Column(String(1000), name="DESC_LOGEMENT", nullable=True)
    pieces = relationship("Piece", backref="logement", cascade="all, delete")
    proprietaires = relationship("Proprietaire", secondary="AVOIR", back_populates="logements", passive_deletes=True)
    
    def __init__(self, id_logement, nom_logement, type_logement, adresse_logement, desc_logement):
        """Init d'un logement

        Args:
            id_logement (int): ID du logement (unique)
            type_logement (enum(str)): "appart" ou "maison"
            adresse_logement (str): Adresse du logmeent 
            desc_logement (str): Description du logement 
        """
        self.id_logement = id_logement
        self.nom_logement = nom_logement
        self.type_logement = type_logement
        self.adresse = adresse_logement
        self.desc_logement = desc_logement


    def __repr__(self):
        """Représentation d'un logement 

        Returns:
            str: Contenant l'ID, le type, et l'adresse
        """
        return "<Logement (%d) %s %s>" % (self.id_logement, self.type_logement,
                                          self.adresse)

    def get_id_logement(self) -> int:
        """Getter de l'ID du logement

        Returns:
            int: ID du logement
        """
        return self.id_logement
    
    def get_nom_logement(self) -> str:
        """Getter du nom du logement

        Returns:
            str: Nom du logement
        """
        return self.nom_logement

    def get_type_logement(self) -> LogementType:
        """Getter du type du logement

        Returns:
            str: Type du logement 
        """
        return self.type_logement

    def get_adresse_logement(self):
        """Getter de l'adresse

        Returns:
            str: Adresse du logement
        """
        return self.adresse


    def get_desc_logement(self):
        """Getter de la descritpion du logement 

        Returns:
            str: Description du logement 
        """
        return self.desc_logement
    
    def set_id_logement(self, id_logement):
        self.id_logement = id_logement

    def set_nom_logement(self, nom_logement):
        self.nom_logement = nom_logement
    
    def set_type_logement(self, type_logement):
        """Changer le type du logement 

        Args:
            type_logement (enum(str)): "maison" ou "appartement"
        """
        self.type_logement = type_logement


    def set_adresse_logement(self, adresse):
        """Changer l'adresse du logement 

        Args:
            adresse (str): nouvelle adresse du logement 
        """
        self.adresse = adresse


    def set_desc_logement(self, desc_logement):
        """Changer la description du logement 

        Args:
            desc_logement (str): nouvelle description du logement 
        """
        self.desc_logement = desc_logement

    def get_pieces_list(self) -> list:
            return Piece.get_pieces_all(self.id_logement)
    
    @staticmethod
    def get_max_id():
        return db.session.query(func.max(Logement.id_logement)).scalar()
    
    @staticmethod
    def next_id() -> int:
        if Logement.get_max_id() is None:
            return 1
        return Logement.get_max_id() + 1
    
    def delete(self, proprio):
        list_assoc = AVOIR.get_biens_by_id(self.id_logement)
        for assoc in list_assoc:
            if assoc.get_id_proprio() == proprio.get_id_proprio():
                assoc.delete()
        last_assoc = AVOIR.get_biens_by_id(self.id_logement)
        list_bien = Bien.get_biens_all(self.id_logement)
        for bien in list_bien:
            if bien.get_id_proprio() == proprio.get_id_proprio():
                bien.delete()
        if len(last_assoc) == 0:
            Piece.query.filter_by(id_logement=self.id_logement).delete()
            db.session.delete(self)
            db.session.commit()
        else:
            print("Le logement est associé à d'autres propriétaires, mais celui ne l'est plus à vous")
        
    @staticmethod
    def put_logement(logement):
            db.session.add(logement)
            db.session.commit()
            
class Piece(Base):
    __tablename__ = "PIECE"

    id_piece = Column(Integer,
                      primary_key=True,
                      nullable=False,
                      name="ID_PIECE")
    nom_piece = Column(String(20), nullable=True, name="NOM_PIECE")
    desc_piece = Column(String(1000), nullable=True, name="DESCRIPTION")
    id_logement = Column(Integer, ForeignKey("LOGEMENT.ID_LOGEMENT",ondelete="CASCADE"), primary_key=True, nullable=False, name="ID_LOGEMENT")
    
    def __init__(self, id_piece, nom_piece, desc_piece, id_logement):
        """Init d'une pièce dans un logement

        Args:
            id_piece (int): id de la pièce
            nom_piece (str): nom de la pièce
            desc_piece (str): description de la pièce
            id_logement (int): id du logement où est contenu la pièce
        """
        self.id_piece = id_piece
        self.nom_piece = nom_piece
        self.desc_piece = desc_piece
        self.id_logement = id_logement


    def __repr__(self):
        """représentation de la pièce

        Returns:
            str: une chaîne de caractère contenant l'id de la pièce ainsi que son nom
        """
        return "<Piece (%d) %s >" % (self.id_piece, self.nom_piece)


    def get_id_piece(self):
        """getter de l'id de la pièce

        Returns:
            int: id de la pièce
        """
        return self.id_piece


    def set_id_piece(self, id_piece):
        self.id_piece = id_piece


    def get_nom_piece(self):
        """getter du nom de la pièce

        Returns:
            str: nom de la pièce
        """
        return self.nom_piece


    def set_nom_piece(self, nom_piece):
        """changer le nom de la pièce

        Args:
            nom_piece (str): Nouveau nom de la pièce 
        """
        self.nom_piece = nom_piece


    def get_desc_piece(self):
        """getter de la description de la pièce 

        Returns:
            str: description de la pièce
        """
        return self.desc_piece


    def set_desc_piece(self, desc_piece):
        """changer la description de la pièce 

        Args:
            desc_piece (str): nouvelle description de la pièce
        """
        self.desc_piece = desc_piece


    def get_id_logement(self):
        """getter de l'id du logement de la pièce

        Returns:
            int: id du logement où est contenu la pièce
        """
        return self.id_logement


    def set_id_logement(self, id_logement):
        self.id_logement = id_logement
    
    
    def get_list_biens(self):
        return Bien.query.filter_by(id_logement=self.id_logement,id_piece=self.id_piece).all()
    
    @staticmethod
    def get_max_id():
        return db.session.query(func.max(Piece.id_piece)).scalar()
    
    @staticmethod
    def next_id() -> int:
        if Piece.get_max_id() is None:
            return 1
        return Piece.get_max_id() + 1
    
    def delete(self):
        Bien.query.filter_by(id_piece=self.id_piece).delete()
        db.session.delete(self)
        db.session.commit()
        
    @staticmethod
    def put_piece(piece):
        db.session.add(piece)
        db.session.commit()
    
    @staticmethod
    def get_pieces_all(id_log):
        return Piece.query.filter_by(id_logement=id_log).all()
        

class Bien(Base):
    __tablename__ = "BIEN"


    id_bien = Column(Integer, name="ID_BIEN", primary_key=True)
    nom_bien = Column(String(100), name="NOM_BIEN", nullable=False)
    date_achat = Column(Date, name="DATE_ACHAT", nullable=True)
    prix = Column(Float, name="PRIX", nullable=True)
    id_proprio = Column(Integer, ForeignKey("PROPRIETAIRE.ID_PROPRIO", ondelete="CASCADE"), nullable=False, name="ID_PROPRIO")
    id_piece = Column(Integer, ForeignKey("PIECE.ID_PIECE", ondelete="CASCADE"), nullable=False, name="ID_PIECE")
    id_logement = Column(Integer, ForeignKey("PIECE.ID_LOGEMENT", ondelete="CASCADE"), nullable=False, name="ID_LOGEMENT")
    id_type = Column(Integer, ForeignKey("TYPEBIEN.ID_TYPE_BIEN"), nullable=False, name="ID_TYPE_BIEN")
    id_cat = Column(Integer, ForeignKey("CATEGORIE.ID_CATEGORIE"), nullable=False, name="ID_CATEGORIE")
    # piece = relationship("Piece", backref="biens", uselist=False, cascade="all, delete")
    
    
    def __init__(self, id_bien, nom_bien, id_proprio, date_achat, prix, id_piece, id_logement,  id_type, id_cat):
        """_summary_

        Args:
            id_bien (int): id du bien (unique)
            nom_bien (str): nom du bien
            id_proprio (int): id du propriétaire du bien
            date_achat (str): date de l'achat du bien
            prix (float): prix à l'achat du bien
            id_piece (int): id de la pièece où est situé le bien
            id_type (int): 
            id_cat (int): _description_
        """
        self.id_bien = id_bien
        self.nom_bien = nom_bien
        self.date_achat = date_achat
        self.prix = prix
        self.id_proprio = id_proprio
        self.id_piece = id_piece
        self.id_logement = id_logement
        self.id_type = id_type
        self.id_cat = id_cat


    def __repr__(self):
        return "<Bien (%d) %s>" % (self.id_bien, self.nom_bien)


    def get_id_bien(self):
        return self.id_bien
    
    def get_nom_bien(self):
        return self.nom_bien


    def set_nom_bien(self, nom_bien):
        self.nom_bien = nom_bien


    def get_date_achat(self):
        return self.date_achat


    def set_date_achat(self, date_achat):
        self.date_achat = date_achat


    def get_prix(self):
        return self.prix


    def set_prix(self, prix):
        self.prix = prix


    def get_id_proprio(self):
        return self.id_proprio
    
    def get_id_piece(self):
        return self.id_piece
    
    def get_id_type(self):
        return self.id_type
    def get_id_cat(self):
        return self.id_cat

    def get_id_logement(self):
        return self.id_logement

    def set_id_logement(self, id_logement):
        self.id_logement = id_logement

    def delete(self):
        Justificatif.query.filter_by(id_bien=self.id_bien).delete()
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_max_id():
        return db.session.query(func.max(Bien.id_bien)).scalar()
    
    @staticmethod
    def next_id():
        if Bien.get_max_id() is None:
            return 1
        return Bien.get_max_id() + 1
    
    def get_nom_logement_by_bien(self, id_bien):
        bien = Bien.query.filter_by(id_bien=id_bien).first()
        return Logement.query.filter_by(id_logement=bien.id_logement).first()
    
    def get_nom_piece_by_bien(self, id_bien):
        bien = Bien.query.filter_by(id_bien=id_bien).first()
        return Piece.query.filter_by(id_piece=bien.id_piece).first()
    
    @staticmethod
    def get_data_bien(id):
        result = Bien.query.filter_by(id_bien=id).first()
        return result
    
    def get_typelogement(self, bien):
        return Logement.query.filter_by(id_logement=bien.id_logement).first()
     
    def get_catbien(self, bien):
        return Categorie.query.filter_by(id_cat=bien.id_cat).first()
    
    def get_typebien(self, bien):
        return TypeBien.query.filter_by(id_type=bien.id_type).first()

    @staticmethod
    def get_biens_by_user(user):
        result = User.query.filter_by(mail=user).first()
        id_proprio = result.proprio.get_id_proprio()
        biens = AVOIR.get_biens_by_proprio(id_proprio)
        non_justifies = Justificatif.possede_justificatif(biens)
        return biens,non_justifies
    
    @staticmethod
    def modifier_bien(id, nom, logement, prix, date, categorie, type):
        result = Bien.query.filter_by(id_bien=id).first()
        result.nom_bien = nom
        result.prix = prix
        result.id_logement = logement
        result.id_cat = categorie
        result.id_type = type
        date_list = date.split("-")
        result.date_achat = datetime.date(int(date_list[0]), int(date_list[1]), int(date_list[2]))
        db.session.commit()
        
    @staticmethod
    def put_bien(bien):
        db.session.add(bien)
        db.session.commit()
        
    def get_justif(self, id):
        return Justificatif.query.filter_by(id_bien=id).first()
    
    @staticmethod
    def get_biens_all(id_log):
        return  Bien.query.filter_by(id_logement=id_log).all()

class AVOIR(Base):
    __tablename__ = "AVOIR"

    id_proprio = Column(Integer, ForeignKey("PROPRIETAIRE.ID_PROPRIO", ondelete="CASCADE"), name="ID_PROPRIO", primary_key=True)
    id_logement = Column(Integer, ForeignKey("LOGEMENT.ID_LOGEMENT", ondelete="CASCADE"), name="ID_LOGEMENT", primary_key=True)

    def __init__(self, id_proprio, id_logement):
        """init d'un lien entre logement et propriétaire

        Args:
            id_proprio (int): id du propriétaire 
            id_logement (int): id du logement 
        """
        self.id_proprio = id_proprio
        self.id_logement = id_logement

    def __repr__(self):
        """représentation du lien entre propriétaire et appartement 

        Returns:
            str : une chaine ce craractère contenant l'id du propriéatire et celuo du logement
        """
        return "Avoir %d %d" % (self.id_proprio, self.id_logement)


    def get_id_proprio(self):
        """getter de l'ID du propriétaire

        Returns:
            int: id du propriétaire
        """
        return self.id_proprio


    def set_id_proprio(self, id_proprio):
        self.id_proprio = id_proprio


    def get_id_logement(self):
        """getter de l'id du logement

        Returns:
            int: id du logement
        """
        return self.id_logement

    def set_id_logement(self, id_logement):
        self.id_logement = id_logement
    
    @staticmethod
    def get_biens_by_proprio(idproprio):
        result = AVOIR.query.filter_by(id_proprio=idproprio)
        liste_biens = []
        for elem in result:
            liste_biens.append(Bien.query.filter_by(id_logement=elem.id_logement).order_by(desc(Bien.id_bien)).all())
        return liste_biens
        

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_biens_by_id(id_log):
        return AVOIR.query.filter_by(id_logement=id_log).all()

    
