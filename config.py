import os

class Config:
    SECRET_KEY = "mi_clave_secreta_segura"
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE = os.path.join(BASEDIR, "database.db")
    UPLOAD_FOLDER = os.path.join(BASEDIR, "static", "uploads")
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # Límite de 2MB por foto
