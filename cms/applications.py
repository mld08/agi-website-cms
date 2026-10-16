"""Réception publique du formulaire de candidature (Coastal Futures).

Le formulaire, servi en statique sur le domaine principal, poste vers cet
endpoint sur le sous-domaine cms. On enregistre en base, on stocke les pièces
dans un dossier PRIVÉ (hors public_html), on notifie par e-mail, puis on redirige
vers la page de confirmation du domaine principal.
"""
import json
import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path

from flask import request, redirect
from werkzeug.utils import secure_filename

from config import Config
from models import db, Application

# Champs texte simples repris tels quels.
_TEXT_FIELDS = [
    "nom", "prenom", "email", "telephone", "date_naissance", "genre",
    "nationalite", "pays_residence", "ville", "tranche_age", "profession",
    "organisation", "langues", "motivation", "experience", "contribution",
]
# Cases à cocher multiples → jointes par « ; ».
_MULTI_FIELDS = ["statut", "domaines"]
# Champs fichier du formulaire → colonne du modèle.
_FILE_FIELDS = {
    "piece_cv": "cv_file",
    "piece_lettre": "lettre_file",
    "piece_identite": "identite_file",
    "piece_projet": "projet_file",
}
# Champs techniques à ignorer (hérités de FormSubmit + champ programme stocké en colonne).
_SKIP = {"_honey", "_captcha", "_subject", "_template", "_next", "programme"}

# Appels Coastal Futures acceptés (sinon on retombe sur "senegal").
_PROGRAMMES = {"senegal", "ghana"}


def _programme_from(form) -> str:
    """Détermine l'appel d'origine : champ caché `programme`, repli sur le sujet."""
    p = (form.get("programme", "") or "").strip().lower()
    if p in _PROGRAMMES:
        return p
    subject = (form.get("_subject", "") or "").lower()
    if "ghana" in subject:
        return "ghana"
    return "senegal"


def register_apply_route(app, csrf):
    @app.route("/apply", methods=["POST"])
    @csrf.exempt
    def apply():
        form = request.form
        redirect_to = _safe_next(form.get("_next", ""))

        # Anti-spam : si le pot de miel est rempli, on fait comme si tout allait bien.
        if form.get("_honey", "").strip():
            return redirect(redirect_to, code=303)

        app_row = Application(
            lang=("en" if "/en/" in form.get("_next", "") else "fr"),
            programme=_programme_from(form),
        )
        for field in _TEXT_FIELDS:
            setattr(app_row, field, form.get(field, "").strip())
        for field in _MULTI_FIELDS:
            setattr(app_row, field, " ; ".join(form.getlist(field)))

        # Toutes les réponses brutes (multi-valeurs incluses).
        raw = {k: (v if len(v) > 1 else v[0])
               for k, v in ((k, form.getlist(k)) for k in form.keys()) if k not in _SKIP}
        app_row.data_json = json.dumps(raw, ensure_ascii=False)

        db.session.add(app_row)
        db.session.commit()   # pour obtenir l'id (utilisé comme dossier des pièces)

        _save_files(app_row)
        db.session.commit()

        _notify(app_row)
        return redirect(redirect_to, code=303)


def _safe_next(url: str) -> str:
    """N'autorise que les redirections vers notre propre site (anti open-redirect)."""
    if url.startswith(Config.SITE_URL + "/"):
        return url
    return f"{Config.SITE_URL}/fr/candidature-envoyee.html"


def _save_files(app_row: Application) -> None:
    dest_dir = Config.APPLICATIONS_DIR / str(app_row.id)
    for form_field, column in _FILE_FIELDS.items():
        f = request.files.get(form_field)
        if not f or not f.filename:
            continue
        ext = Path(f.filename).suffix.lower()
        if ext not in Config.ALLOWED_APP_EXT:
            continue
        f.seek(0, 2); size = f.tell(); f.seek(0)
        if size == 0 or size > Config.MAX_APP_FILE_SIZE:
            continue
        dest_dir.mkdir(parents=True, exist_ok=True)
        # Nom neutre : <champ><ext> (le nom d'origine peut contenir des données perso).
        name = secure_filename(f"{column}{ext}")
        f.save(dest_dir / name)
        setattr(app_row, column, f"{app_row.id}/{name}")


def _notify(app_row: Application) -> None:
    """Envoie un e-mail de notification si le SMTP est configuré (sinon, silencieux)."""
    if not (Config.SMTP_HOST and Config.SMTP_USER and Config.APPLICATION_NOTIFY_EMAIL):
        return
    try:
        msg = EmailMessage()
        msg["Subject"] = f"Nouvelle candidature Coastal Futures — {app_row.full_name()}"
        msg["From"] = Config.SMTP_FROM
        msg["To"] = Config.APPLICATION_NOTIFY_EMAIL
        if app_row.email:
            msg["Reply-To"] = app_row.email
        lines = [
            f"Nom : {app_row.prenom} {app_row.nom}",
            f"E-mail : {app_row.email}",
            f"Téléphone : {app_row.telephone}",
            f"Nationalité : {app_row.nationalite}",
            f"Ville / pays : {app_row.ville} {app_row.pays_residence}",
            f"Tranche d'âge : {app_row.tranche_age}",
            f"Statut : {app_row.statut}",
            f"Domaines : {app_row.domaines}",
            f"Pièces jointes : {', '.join(l for l, _, _ in app_row.files()) or 'aucune'}",
            "",
            "Voir la candidature complète dans l'administration → menu Candidatures.",
        ]
        msg.set_content("\n".join(lines))

        if Config.SMTP_PORT == 465:
            with smtplib.SMTP_SSL(Config.SMTP_HOST, Config.SMTP_PORT,
                                  context=ssl.create_default_context(), timeout=15) as s:
                s.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
                s.send_message(msg)
        else:
            with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT, timeout=15) as s:
                s.starttls(context=ssl.create_default_context())
                s.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
                s.send_message(msg)
    except Exception:  # noqa: BLE001 — une notification ratée ne doit pas casser l'envoi
        pass
