# Importations de modules
from flask_wtf import FlaskForm
from wtforms import *
from mobilist.models.models import *
import os
from wtforms.validators import DataRequired
from .UploadFileForm import UPLOAD_FOLDER_JUSTIFICATIF
from flask_login import login_user , current_user, AnonymousUserMixin


class AjoutBienForm(FlaskForm):
    """
    Formulaire permettant d'ajouter un bien

    Attributes : 
        logement (SelectField) : sélection du logement
        nom_bien (StringField) : le nom du bien
        type_bien (SelectField) : sélection du type
        categorie_bien (SelectField) : sélection de la catégorie
        piece_bien (SelectField) : sélection du nombre de biens
        prix_bien (FloatField) : le prix
        date_bien (DateField) : sélection de la date d'achat
        description_bien (TextAreaField) : la description du bien
        file (FileField) : import d'un fichier concernant le bien
        id_proprio (HiddenField) : identifiant caché du propriétaire
        id_bien (HiddenField) : identifiant caché du bien
    
    Methods : 
        __init__ : Constructeur de la classe, initialise le formulaire

        create_justificatif_bien : Sauvegarde le fichier importé dans le répertoire spécifié

        set_id : Setter de l'identifiant du bien

        get_log_choices, get_type_bien_choices, get_cat_bien_choices : Getters pour le logement, le type et la catégorie du bien
    """
    logement  = SelectField('Logement', validators=[DataRequired()], coerce=int)
    nom_bien = StringField('Nom du bien', validators=[DataRequired()])
    type_bien = SelectField('Type de bien', validators=[DataRequired()],coerce=int)
    categorie_bien = SelectField('Catégorie', validators=[DataRequired()], coerce=int)
    piece_bien = SelectField('Nombre de pièces', validators=[DataRequired()], coerce=int)
    prix_bien = FloatField('Prix neuf', validators=[DataRequired()])
    date_bien = DateField("Date de l'achat", validators=[DataRequired()])
    description_bien = TextAreaField('Description')
    file = FileField('File')
    id_proprio = HiddenField("id_proprio") 
    id_bien = HiddenField("id_proprio")

    def __init__(self,*args, **kwargs):
        """
        Constructeur de la classe, initialise le formulaire
        """
        super(AjoutBienForm, self).__init__(*args, **kwargs)
        self.id_bien = None
        self.id_proprio = current_user.id_user
        self.logement.choices = [(l.get_id_logement(), l.get_nom_logement()) for l in Proprietaire.query.get(current_user.id_user).logements]
        self.type_bien.choices = [(t.id_type, t.nom_type) for t in TypeBien.query.all()]
        self.categorie_bien.choices = [(c.get_id_cat(), c.get_nom_cat()) for c in Categorie.query.all()]
        self.piece_bien.choices = [(p.get_id_piece(), p.get_nom_piece()) for p in Piece.query.all()]

    def create_justificatif_bien(self) -> str:
        """
        Sauvegarde le fichier importé dans le répertoire spécifié
        """
        try:
            file = self.file.data
            if not os.path.exists(os.path.join(UPLOAD_FOLDER_JUSTIFICATIF, str(current_user.id_user))): # creation du dossier de l'utilisateur si inexistant
                os.makedirs(os.path.join(UPLOAD_FOLDER_JUSTIFICATIF, str(current_user.id_user)))
            CUSTOM_UPLOAD_FOLDER_JUSTIFICATIF = os.path.join(UPLOAD_FOLDER_JUSTIFICATIF, str(current_user.id_user))
            file.save(os.path.join(CUSTOM_UPLOAD_FOLDER_JUSTIFICATIF, secure_filename(file.filename)))
            print("file saved")
            return os.path.join(CUSTOM_UPLOAD_FOLDER_JUSTIFICATIF, file.filename) # retourne le chemin du fichier, pour l'enregistrement en BD
        except Exception as e:
            print("erreur:", e)

    def set_id(self,id):
        """
        Setter de l'identifiant du bien
        """
        self.id_bien = id
    
    def get_log_choices(self,nom) -> str:
        """
        Getter du logement choisi
        """
        for elem in self.logement.choices:
            if elem[1]==nom:
                return elem[0]
        return ""

    def get_type_bien_choices(self, nom) -> str:
        """
        Getter du type de bien choisi
        """
        for elem in self.type_bien.choices:
            if elem[1]==nom:
                return elem[0]
        return ""

    def get_cat_bien_choices(self, nom) -> str:
        """
        Getter de la catégorie du bien choisi
        """ 
        for elem in self.categorie_bien.choices:
            if elem[1]==nom:
                return elem[0]
        return ""

    def __str__(self) -> str:
        return "Form Bien, values :"+self.nom_bien.data
