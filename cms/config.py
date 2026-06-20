"""Configuration centrale du CMS.

En local (aucune variable DATABASE_URL), on bascule automatiquement sur SQLite
pour pouvoir tout tester sous Windows sans installer MySQL. En production cPanel,
on renseigne DATABASE_URL avec la base MySQL créée dans cPanel.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Dossiers de référence.
BASE_DIR = Path(__file__).resolve().parent          # .../cms
PROJECT_DIR = BASE_DIR.parent                        # .../AGI-Website
TEMPLATE_DIR = PROJECT_DIR / "template"              # le site statique d'origine (design source)

# Charge le fichier .env s'il existe.
load_dotenv(BASE_DIR / ".env")


def _database_url() -> str:
    url = os.environ.get("DATABASE_URL", "").strip()
    if url:
        return url
    # Défaut local : SQLite dans le dossier instance/.
    instance = BASE_DIR / "instance"
    instance.mkdir(exist_ok=True)
    return f"sqlite:///{(instance / 'cms.db').as_posix()}"


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-a-changer")
    SQLALCHEMY_DATABASE_URI = _database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Génération du site.
    SITE_URL = os.environ.get("SITE_URL", "https://africagovernanceinstitute.org").rstrip("/")
    OUTPUT_DIR = Path(
        os.environ.get("OUTPUT_DIR")
        or (PROJECT_DIR / "public")
    ).resolve()
    TEMPLATE_DIR = TEMPLATE_DIR

    # Uploads (images + documents). Copiés vers public/assets/uploads à la génération.
    UPLOAD_DIR = BASE_DIR / "uploads"
    ALLOWED_IMAGE_EXT = {".webp", ".jpg", ".jpeg", ".png", ".gif", ".svg"}
    ALLOWED_DOC_EXT = {".pdf"}
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024   # 25 Mo max par fichier
