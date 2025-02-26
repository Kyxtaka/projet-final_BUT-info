from mobilist.app import app, db
from .views import *
from .login import *
from .login import login_view
from .uploadfile import upload
from .logements import logements
from .biens import biens
from .admin import admin
from .admin import utilisateurs


app.register_blueprint(login_view.bp)
app.register_blueprint(upload.upload_bp)
app.register_blueprint(logements.logements_bp)
app.register_blueprint(biens.biens_bp)
app.register_blueprint(admin.admin_bp)
app.register_blueprint(utilisateurs.utilisateur_bp)