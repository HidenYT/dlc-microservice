from flask import Blueprint

bp = Blueprint("api", __name__, url_prefix="/api")

from . import models
from . import routers
from . import error_handlers