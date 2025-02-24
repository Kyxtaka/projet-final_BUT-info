from mobilist.app import app, db
from .views import *
from flask import Blueprint
from .login import *
from .uploadfile import upload


app.register_blueprint(login_view.bp)
app.register_blueprint(upload.upload_bp)