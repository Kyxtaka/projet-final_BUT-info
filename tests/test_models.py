import unittest

from mobilist.models.classes.User import User
from mobilist.models.classes.TypeBien import TypeBien
from mobilist.models.classes.Proprietaire import Proprietaire
from mobilist.models.classes.Logement import Piece
from mobilist.models.classes.Logement import LogementType
from mobilist.models.classes.Logement import Logement
from mobilist.models.classes.Justificatif import Justificatif
from mobilist.models.classes.Categorie import Categorie
from mobilist.models.classes.Logement import Bien
from mobilist.models.classes.Logement import AVOIR
from mobilist.models.classes.Avis import Avis
from mobilist.models.models import *
from hashlib import sha256
from flask import Flask
from flask_sqlalchemy  import SQLAlchemy
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
import datetime
from flask import session
from mobilist.models.models import set_base
import pytest
# from .secure_constante import *
import os
from mobilist.app import mkpath, app, db


class UserTest(unittest.TestCase):

   def setUp(self):
      with app.app_context():
        self.db_uri = ('sqlite:///'+mkpath('DBMOBILIST.db'))
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = self.db_uri
        self.app = app.test_client()
        set_base(db)
        db.drop_all()
        db.create_all()
        
   def test_proprietaire(self):
      with app.app_context():
         proprio = Proprietaire(1,"johnkevin@email.com", "John", "Kevin")
         user = User("johnkevin@email.com", "123", "proprietaire", 1)
         Proprietaire.put_proprio(proprio)
         User.put_user(user)
         
         proprio_john  = db.session.get(Proprietaire,1)
         self.assertEqual(proprio.nom, proprio_john.nom)
         self.assertEqual(proprio_john.nom, "John")
         self.assertEqual(proprio_john.prenom, "Kevin")

         self.assertEqual(proprio.get_id_proprio(), 1)
         self.assertEqual(proprio.get_nom(), "John")
         self.assertEqual(proprio.get_prenom(), "Kevin")
         
         proprio.set_prenom("Patrick")
         self.assertEqual(proprio.get_prenom(), "Patrick")
         proprio.set_nom("Dupont")
         self.assertEqual(proprio.get_nom(), "Dupont")
         self.assertEqual( Proprietaire.max_id(),1)
         self.assertEqual(Proprietaire.get_by_mail("johnkevin@email.com"), proprio)
         self.assertEqual(Proprietaire.get_by_nom("Dupont"), [proprio])

   def test_user(self):
      with app.app_context():
         proprio = Proprietaire(2,"trixymartin@email.com", "Martin", "Trixy")
         mdp = "123"
         m = sha256()
         m.update(mdp.encode())
         passwd = m.hexdigest()
         user = User("trixymartin@email.com", passwd, "proprietaire", 2)
         
         Proprietaire.put_proprio(proprio)
         User.put_user(user)
         user.set_proprio(proprio)

         self.assertEqual(user.get_role(), "proprietaire")
         user.set_role("administrateur")
         self.assertEqual(user.get_role(), "administrateur")
         
         User.modifier("trixymartin@email.com", "Valin", "Ophelie")
         self.assertEqual(proprio.get_nom(), "Valin")
         self.assertEqual(proprio.get_prenom(), "Ophelie")

         admin = User("admin@mail.com", "123", "admin", 3)
         User.put_user(admin)
         
   def test_bien(self):
      with app.app_context():
         logement = Logement(1,"maison 1","MAISON","1 rue","grande maison")
         piece = Piece(1,"salon","grande piece",1)
         typebien = TypeBien(1,"meuble")
         cat = Categorie(1,"meuble")
         bien = Bien(1,"chaise",2,datetime.date(2024, 11, 12), 19.99, 1,1,1,1)
         TypeBien.put_type(typebien)
         Categorie.put_categorie(cat)
         Logement.put_logement(logement)
         Piece.put_piece(piece)
         Bien.put_bien(bien)
         bien2 = Bien(2,"chaise",2,datetime.date(2024, 11, 12), 19.99, 1,1,1,1)
         Bien.put_bien(bien2)
         self.assertEqual(bien.get_date_achat(), datetime.date(2024, 11, 12))
         self.assertEqual(bien.get_id_bien(), 1)
         self.assertEqual(bien.get_prix(), 19.99)
         self.assertEqual(bien.get_id_cat(),1)
         self.assertEqual(bien.get_nom_bien(), "chaise")

         bien.set_id_logement(2)
         bien.set_date_achat(datetime.date(2024,11,11))
         self.assertEqual(bien.get_date_achat(), datetime.date(2024, 11, 11))
         bien.set_nom_bien("chaise 1")
         self.assertEqual(bien.get_nom_bien(), "chaise 1")
         bien.set_prix(19.98)
         self.assertEqual(bien.get_prix(), 19.98)
         
      
   def test_logement(self):
      with app.app_context():
         logement = Logement(2,"maison 2","MAISON","2 rue","grande maison")
         self.assertEqual(logement.get_adresse_logement(), "2 rue")
         self.assertEqual(logement.get_id_logement(),2)
         self.assertEqual(logement.get_type_logement(), "MAISON")
         self.assertEqual(logement.get_desc_logement(), "grande maison")

   def test_logement_set(self):
         with app.app_context():
            logement = Logement(2,"maison 2","MAISON","2 rue","grande maison")
            logement.set_id_logement(3)
            self.assertEqual(logement.get_id_logement(),3)
            logement.set_adresse_logement("3 rue perdu")
            self.assertEqual(logement.get_adresse_logement(), "3 rue perdu")
            logement.set_nom_logement("mon logement")
            self.assertEqual(logement.get_nom_logement(), "mon logement")
            logement.set_type_logement("APPART")
            self.assertEqual(logement.get_type_logement(), "APPART")
            Logement.put_logement(logement)
            self.assertEqual(logement.get_max_id(), 3)
            self.assertEqual(logement.next_id(),4)
         
   def test_piece(self):
      with app.app_context():
         piece = Piece(2,"garage","grande piece",1)
         self.assertEqual(piece.get_desc_piece(), "grande piece")
         self.assertEqual(piece.get_id_piece(), 2)
         self.assertEqual(piece.get_nom_piece(), "garage")
         self.assertEqual(piece.get_id_logement(),1)
      
   def test_piece_set(self):
         with app.app_context():
            piece = Piece(2,"garage","grande piece",1)
            piece.set_desc_piece("grande grande piece")
            self.assertEqual(piece.get_desc_piece(), "grande grande piece")
            piece.set_id_logement(2)
            piece.set_nom_piece("cellier")
            self.assertEqual(piece.get_nom_piece(), "cellier")
            Piece.put_piece(piece)
            self.assertEqual(Piece.get_max_id(), 2)
            self.assertEqual(Piece.next_id(), 3)
   
   def test_typebien(self):
      with app.app_context():
         typebien = TypeBien(2,"électroménager")
         self.assertEqual(typebien.get_id_type(), 2)
         self.assertEqual(typebien.get_nom_type(), "électroménager")
         typebien.set_nom_type("electromenager")
         typebien.set_id_type(3)
         TypeBien.put_type(typebien)
   
   def test_categorie(self):
      with app.app_context():
         cat = Categorie(2, "accessoire cuisine")
         self.assertEqual(cat.get_id_cat(),2)
         self.assertEqual(cat.get_nom_cat(), "accessoire cuisine")
         cat.set_id_cat(3)
         cat.set_nom_cat("accesoire")
   
   def test_avis(self):
      with app.app_context():
         avis = Avis(1, "trop bien !", 2)
         self.assertEqual(avis.get_id_avis(),1)
         self.assertEqual(avis.get_desc_avis(), "trop bien !")
         self.assertEqual(avis.get_id_proprio(), 2)

   def test_avis_set(self):
         with app.app_context():
            avis = Avis(1, "trop bien !", 2)
            avis.set_desc_avis("trop trop bien !")
            self.assertEqual(avis.get_desc_avis(), "trop trop bien !")
            avis.set_id_avis(2)
            avis.set_id_proprio(1)
            Avis.ajoute(avis)
            self.assertEqual(Avis.max_id(),2)

   def test_justificatif(self):
      with app.app_context():
         justif = Justificatif(1,"mon justif",  datetime.date(2024, 11, 11), "url", 1)
         self.assertEqual(justif.get_id_justif(), 1)
         self.assertEqual(justif.get_id_bien(),1)
         self.assertEqual(justif.get_date_ajout(), datetime.date(2024, 11, 11))
         self.assertEqual(justif.get_nom_justif(), "mon justif")
         self.assertEqual(justif.get_URL(), "url")
      
   def test_justificatif_set(self):
         with app.app_context():
            justif = Justificatif(1,"mon justif",  datetime.date(2024, 11, 11), "url", 1)
            justif.set_date_ajout(datetime.date(2024,11,12))
            justif.set_id_justif(2)
            justif.set_URL("urll")
            justif.set_nom_justif('mon justiff')
            justif.put_justificatif(justif)
            self.assertEqual(Justificatif.next_id(), 3)
            self.assertEqual(Justificatif.get_max_id(), 2)


   def test_password_token(self):
      with app.app_context():
         token = ChangePasswordToken("trixymartin@email.com")
         self.assertEqual(token.is_expired(), False)
         token.set_used()
         ChangePasswordToken.get_by_token("123")
         

if __name__ == '__main__':
   unittest.main()