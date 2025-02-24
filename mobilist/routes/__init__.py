from mobilist.app import app, db
from .views import *
from flask import Blueprint
from .login import *


app.register_blueprint(login_view.bp)