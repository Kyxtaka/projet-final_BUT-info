
from flask_wtf import FlaskForm
from wtforms import *
from PyPDF2 import PdfReader
import os
from mobilist.app import app
from wtforms.validators import DataRequired


#constante : chemin d'acces au dossier de telechargement des justificatifs
UPLOAD_FOLDER_JUSTIFICATIF = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    app.config['UPLOAD_FOLDER'],
    'justificatifs'
)

class UploadFileForm(FlaskForm):
    """
    Formulaire permettant à un utilisateur d'importer un fichier

    Attributes :
        file (FileField) : Champ pour importer un fichier

    Methods :
        __init__ : Constructeur de la classe, initialise le formulaire
        validate_file_format : Validation pour vérifier que le fichier importé a un format autorisé (PDF, PNG, JPG et JPEG), 
                               et que la longueur du nom est moins de 50 caractères

        validate_file_size : Validation pour vérifier que la taille du fichier importé ne dépasse pas 1 Mo

        create_justificatif_bien : Sécurise le nom du fichier importé, et le sauvegarde dans le dossier indiqué

        lire_pdf : Lit un fichier PDF et extrait son texte
    """
    file = FileField('File', validators=[DataRequired()])

    def __init__(self,*args, **kwargs):
        """
        Constructeur de la classe, initialise le formulaire
        """
        super(UploadFileForm, self).__init__(*args, **kwargs)


    def validate_file_format(self, form, field):
        """
        Vérifie que le fichier importé a un format autorisé (PDF, PNG, JPG et JPEG), et que la longueur de son nom ne dépasse pas 50 caractères
        """
        filename = field.data
        print("form:", form)
        print("field:", field)
        print("field.data:", field.data)

        if filename:
            print("filname:", filename)
            if not (filename.endswith(".pdf") or filename.endswith(".png") or filename.endswith(".jpg") or filename.endswith(".jpeg")):
                raise ValidationError("Le fichier doit être de type PDF, PNG, JPG ou JPEG")
            elif len(filename) > 50:
                raise ValidationError("Le nom du fichier est trop long")
        else:
            raise ValidationError("Le fichier est vide")

    def validate_file_size(self, field):
        """
        Vérifie si la taille du fichier importé ne dépasse pas 1 Mo
        """
        file = field.data
        if file:
            if len(file.read()) > 1000000:
                raise ValidationError("Le fichier est trop volumineux")
        else:
            raise ValidationError("Le fichier est vide")

    def create_justificatif_bien(self):
        """
        Sécurise le nom du fichier importé, puis le sauvegarde dans le répertoire spécifié par 'UPLOAD_FOLDER_JUSTIFICATIF'
        """
        try:
            file = self.file.data
            file.save(os.path.join(UPLOAD_FOLDER_JUSTIFICATIF, secure_filename(file.filename)))
            print("file saved")
        except Exception as e:
            print("erreur:", e)


    def lire_pdf(self,fichier):
        """
        Lit un fichier PDF et extrait son texte

        Attributes : 
            fichier (str) : le chemin du fichier PDF

        Returns : 
            texte (str) : le texte extrait
        """
        reader = PdfReader(fichier)
        texte = ""
        for page in reader.pages:
            texte += page.extract_text()
        return texte