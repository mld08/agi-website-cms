"""Configuration centrale du CMS.

En local (aucune variable DATABASE_URL), on bascule automatiquement sur SQLite
pour pouvoir tout tester sous Windows sans installer MySQL. En production cPanel,
on renseigne DATABASE_URL avec la base MySQL créée dans cPanel.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Dossiers de référence.
BASE_DIR = Path(__file__).resolve().parent          # dossier de l'app (cms/ en local)
PROJECT_DIR = BASE_DIR.parent                        # parent (AGI-Website en local, home sur le serveur)

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
    # Évite les erreurs 500 « MySQL server has gone away » : on teste la connexion
    # avant chaque usage (reconnexion transparente) et on recycle les connexions
    # avant que MySQL ne les ferme pour inactivité.
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }

    # Installation web sans terminal : jeton secret + identifiants du 1er admin.
    # Laissez SETUP_TOKEN vide pour DÉSACTIVER la page /setup (recommandé après install).
    SETUP_TOKEN = os.environ.get("SETUP_TOKEN", "").strip()
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "").strip().lower()
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")

    # Génération du site.
    SITE_URL = os.environ.get("SITE_URL", "https://africagovernanceinstitute.org").rstrip("/")
    # Dossier de sortie du site généré (en prod : public_html). Défaut local : ../public
    OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR") or (PROJECT_DIR / "public")).resolve()
    # Dossier du site d'origine (design source). Surchargé par .env en prod.
    TEMPLATE_DIR = Path(os.environ.get("TEMPLATE_DIR") or (PROJECT_DIR / "template")).resolve()

    # Uploads (images + documents). Copiés vers public/assets/uploads à la génération.
    UPLOAD_DIR = BASE_DIR / "uploads"
    ALLOWED_IMAGE_EXT = {".webp", ".jpg", ".jpeg", ".png", ".gif", ".svg"}
    ALLOWED_DOC_EXT = {".pdf"}
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024   # 25 Mo max par requête

    # Candidatures (formulaire public). Pièces stockées en PRIVÉ, hors public_html.
    APPLICATIONS_DIR = BASE_DIR / "applications_files"
    ALLOWED_APP_EXT = {".pdf", ".doc", ".docx", ".jpg", ".jpeg", ".png"}
    MAX_APP_FILE_SIZE = 10 * 1024 * 1024    # 10 Mo max par pièce jointe

    # Notification e-mail des nouvelles candidatures (SMTP cPanel).
    SMTP_HOST = os.environ.get("SMTP_HOST", "").strip()
    SMTP_PORT = int(os.environ.get("SMTP_PORT", "465") or 465)
    SMTP_USER = os.environ.get("SMTP_USER", "").strip()
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
    SMTP_FROM = os.environ.get("SMTP_FROM", "").strip() or os.environ.get("SMTP_USER", "").strip()
    APPLICATION_NOTIFY_EMAIL = os.environ.get("APPLICATION_NOTIFY_EMAIL", "").strip()
