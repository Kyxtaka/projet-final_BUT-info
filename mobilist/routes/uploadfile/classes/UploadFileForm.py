
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
    file = FileField('File', validators=[DataRequired()])

    def __init__(self,*args, **kwargs):
        super(UploadFileForm, self).__init__(*args, **kwargs)
        #########################################################
        # print(f"**********************************\n {self.file.validators} \n**********************************")
        # if self.validate_file_format not in self.file.validators:
        #     self.file.validators = (self.validate_file_format,) +  tuple(self.file.validators)
        # print(f"**********************************\n {self.file.validators} \n**********************************")
        #########################################################

    def validate_file_format(self, form, field):
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

    def validate_file_size(self, form, field):
        file = field.data
        if file:
            if len(file.read()) > 1000000:
                raise ValidationError("Le fichier est trop volumineux")
        else:
            raise ValidationError("Le fichier est vide")

    def create_justificatif_bien(self):
        try:
            file = self.file.data
            file.save(os.path.join(UPLOAD_FOLDER_JUSTIFICATIF, secure_filename(file.filename)))
            print("file saved")
        except Exception as e:
            print("erreur:", e)


    def lire_pdf(self,fichier):
        reader = PdfReader(fichier)
        texte = ""
        for page in reader.pages:
            texte += page.extract_text()
        return texte