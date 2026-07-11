"""Application Flask du CMS.

Phase 1 : génération du site statique (CLI).
Phase 2 : tableau de bord d'administration en français (connexion, édition
d'articles, upload d'images, bouton « Générer le site »).

Commandes (depuis le dossier cms/, après « pip install -r requirements.txt ») :
    flask --app app init-db                         # crée les tables
    flask --app app seed                            # insère les 3 articles existants
    flask --app app create-user EMAIL MOTDEPASSE    # crée un compte admin
    flask --app app build                           # génère le site statique
    flask --app app rebuild                          # init-db + seed + build
    flask --app app run                              # lance l'admin (http://127.0.0.1:5000/admin)
"""
import os
import click
from flask import Flask, redirect, url_for, abort
from markupsafe import escape
from flask_login import LoginManager
from flask_wtf import CSRFProtect

from config import Config
from models import db, User

login_manager = LoginManager()
csrf = CSRFProtect()


def create_app(config: type = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    csrf.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "admin.login"
    login_manager.login_message = "Veuillez vous connecter pour accéder à l'administration."

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Routes & blueprints
    from admin import admin as admin_bp, register_media_route
    app.register_blueprint(admin_bp)
    register_media_route(app)

    # Endpoint public du formulaire de candidature (exempté de CSRF).
    from applications import register_apply_route
    register_apply_route(app, csrf)

    @app.route("/")
    def home():
        return redirect(url_for("admin.dashboard"))

    @app.route("/setup/<token>")
    def first_run_setup(token):
        """Installation sans terminal (à usage unique).

        Protégée par SETUP_TOKEN (.env). Crée les tables, insère le contenu de
        départ, crée le 1er compte admin (ADMIN_EMAIL / ADMIN_PASSWORD) et génère
        le site. Idempotente. Désactivez-la ensuite en vidant SETUP_TOKEN.
        """
        if not Config.SETUP_TOKEN or token != Config.SETUP_TOKEN:
            abort(404)

        from seed import seed_articles, seed_team, seed_programs, seed_resources
        from generator import build_site
        from dbtools import sync_schema
        lines = []
        try:
            created, added = sync_schema()
            lines.append(f"Tables créées : {', '.join(created) if created else 'aucune (déjà à jour)'}")
            lines.append(f"Colonnes ajoutées : {', '.join(added) if added else 'aucune (déjà à jour)'}")
            lines.append(f"Articles ajoutés : {seed_articles()}")
            lines.append(f"Membres ajoutés : {seed_team()}")
            lines.append(f"Programmes ajoutés : {seed_programs()}")
            lines.append(f"Ressources ajoutées : {seed_resources()}")

            if Config.ADMIN_EMAIL and Config.ADMIN_PASSWORD:
                user = User.query.filter_by(email=Config.ADMIN_EMAIL).first()
                if user is None:
                    user = User(email=Config.ADMIN_EMAIL, role="admin")
                    user.set_password(Config.ADMIN_PASSWORD)
                    db.session.add(user)
                    db.session.commit()
                    lines.append(f"Compte admin créé : {Config.ADMIN_EMAIL}")
                else:
                    lines.append(f"Compte admin déjà présent : {Config.ADMIN_EMAIL}")
            else:
                lines.append("ADMIN_EMAIL / ADMIN_PASSWORD non renseignés : aucun compte créé.")

            written = build_site()
            lines.append(f"Site généré : {len(written)} page(s) dans {Config.OUTPUT_DIR}")
            ok = True
        except Exception as exc:  # noqa: BLE001 — on affiche l'erreur (pas de terminal)
            db.session.rollback()
            lines.append(f"ERREUR : {exc!r}")
            ok = False

        body = "".join(f"<li>{escape(l)}</li>" for l in lines)
        note = ("<p style='color:#3F4A18'><strong>Installation terminée.</strong> "
                "Pour sécuriser, videz <code>SETUP_TOKEN</code> dans le .env puis redémarrez l'app. "
                "<a href='/admin'>Aller à l'administration →</a></p>") if ok else \
               ("<p style='color:#8E1F1A'><strong>Échec.</strong> Corrigez le problème ci-dessus "
                "(souvent : DATABASE_URL, TEMPLATE_DIR ou OUTPUT_DIR dans le .env) puis rechargez.</p>")
        return (f"<!doctype html><meta charset='utf-8'><title>Installation AGI CMS</title>"
                f"<div style=\"font-family:system-ui;max-width:680px;margin:48px auto;padding:0 20px;"
                f"color:#181612;line-height:1.6\"><h1 style='font-size:1.6rem'>Installation AGI CMS</h1>"
                f"<ul>{body}</ul>{note}</div>"), (200 if ok else 500)

    _register_cli(app)
    return app


def _register_cli(app: Flask) -> None:
    from generator import build_site
    from seed import seed_articles, seed_team, seed_programs, seed_resources

    @app.cli.command("init-db")
    def init_db():
        """Crée les tables de la base."""
        db.create_all()
        click.echo(f"Base initialisée : {app.config['SQLALCHEMY_DATABASE_URI']}")

    @app.cli.command("seed")
    def seed():
        """Insère les contenus de départ (articles, équipe, programmes, ressources)."""
        na, nt = seed_articles(), seed_team()
        npr, nr = seed_programs(), seed_resources()
        click.echo(f"{na} article(s), {nt} membre(s), {npr} programme(s), {nr} ressource(s) ajouté(s).")

    @app.cli.command("create-user")
    @click.argument("email")
    @click.argument("password")
    @click.option("--role", default="admin", help="admin ou editor")
    def create_user(email, password, role):
        """Crée (ou met à jour) un compte d'administration."""
        email = email.strip().lower()
        user = User.query.filter_by(email=email).first()
        if user is None:
            user = User(email=email, role=role)
            db.session.add(user)
        user.role = role
        user.set_password(password)
        db.session.commit()
        click.echo(f"Compte prêt : {email} ({role})")

    @app.cli.command("build")
    def build():
        """Génère le site statique dans OUTPUT_DIR."""
        written = build_site()
        click.echo(f"Site généré dans : {app.config['OUTPUT_DIR']}")
        for page in written:
            click.echo(f"  régénéré : {page}")

    @app.cli.command("rebuild")
    def rebuild():
        """Tout en un : crée les tables, insère le seed, génère le site."""
        db.create_all()
        na, nt = seed_articles(), seed_team()
        npr, nr = seed_programs(), seed_resources()
        written = build_site()
        click.echo(f"Tables OK · {na} article(s), {nt} membre(s), {npr} programme(s), {nr} ressource(s) · {len(written)} page(s).")
        click.echo(f"Site dans : {app.config['OUTPUT_DIR']}")


# Instance au niveau module pour « flask --app app » et pour Passenger (cPanel).
app = create_app()


if __name__ == "__main__":
    app.run(debug=True, port=5000)
