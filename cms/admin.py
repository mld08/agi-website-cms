"""Tableau de bord d'administration (Phase 2).

Interface en français pour une équipe non-technique :
  - connexion sécurisée (Flask-Login) ;
  - liste des articles, création / édition / suppression ;
  - éditeur visuel (WYSIWYG) pour le corps des articles ;
  - upload d'images (dimensions détectées automatiquement) ;
  - bouton « Générer le site » qui régénère le HTML statique.
"""
import re
import unicodedata
from functools import wraps
from datetime import date, datetime
from pathlib import Path

from flask import (Blueprint, render_template, request, redirect, url_for,
                   flash, jsonify, send_from_directory, abort, current_app)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename

from config import Config
from models import db, Article, User, TeamMember, Program, Resource, PublishLog
from generator import build_site

admin = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(view):
    """Réserve une vue aux comptes de rôle « admin » (gestion des utilisateurs)."""
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if getattr(current_user, "role", "") != "admin":
            abort(403)
        return view(*args, **kwargs)
    return wrapped

# Champs texte simples repris tels quels depuis le formulaire (le slug est traité à part).
_TEXT_FIELDS = [
    "author", "image",
    "image_alt_en", "image_alt_fr",
    "category_en", "category_fr",
    "title_en", "title_fr",
    "body_en", "body_fr",
    "meta_description_en", "meta_description_fr",
]


# --------------------------------------------------------------------------- #
#  Authentification
# --------------------------------------------------------------------------- #
@admin.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(request.args.get("next") or url_for("admin.dashboard"))
        flash("Identifiants incorrects.", "error")
    return render_template("admin/login.html")


@admin.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("admin.login"))


# --------------------------------------------------------------------------- #
#  Tableau de bord
# --------------------------------------------------------------------------- #
@admin.route("/")
@login_required
def dashboard():
    articles = Article.query.order_by(Article.pub_date.desc(), Article.id.desc()).all()
    return render_template("admin/dashboard.html", articles=articles)


@admin.route("/articles/new", methods=["GET", "POST"])
@login_required
def article_new():
    if request.method == "POST":
        article = Article(pub_date=date.today())
        _apply_form(article)
        db.session.add(article)
        db.session.commit()
        flash("Article créé. Pensez à « Générer le site » pour le mettre en ligne.", "ok")
        return redirect(url_for("admin.article_edit", article_id=article.id))
    return render_template("admin/article_form.html", article=None)


@admin.route("/articles/<int:article_id>/edit", methods=["GET", "POST"])
@login_required
def article_edit(article_id):
    article = Article.query.get_or_404(article_id)
    if request.method == "POST":
        _apply_form(article)
        db.session.commit()
        flash("Modifications enregistrées.", "ok")
        return redirect(url_for("admin.article_edit", article_id=article.id))
    return render_template("admin/article_form.html", article=article)


@admin.route("/articles/<int:article_id>/delete", methods=["POST"])
@login_required
def article_delete(article_id):
    article = Article.query.get_or_404(article_id)
    db.session.delete(article)
    db.session.commit()
    flash("Article supprimé.", "ok")
    return redirect(url_for("admin.dashboard"))


@admin.route("/articles/<int:article_id>/preview")
@login_required
def article_preview(article_id):
    """Prévisualise un article (même brouillon) sans le publier sur le site."""
    article = Article.query.get_or_404(article_id)
    lang = request.args.get("lang", "fr")
    if lang not in ("en", "fr"):
        lang = "fr"
    out = Config.OUTPUT_DIR
    # Les assets (CSS, images) doivent exister : on génère le site si nécessaire.
    if not (out / "styles.css").exists():
        build_site()
    from generator import render_detail
    target = out / lang / "_preview.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_detail(article, lang), encoding="utf-8")
    return redirect(url_for("preview_file", filename=f"{lang}/_preview.html"))


# --------------------------------------------------------------------------- #
#  Équipe
# --------------------------------------------------------------------------- #
_TEAM_TEXT_FIELDS = [
    "name_en", "name_fr", "role_en", "role_fr",
    "photo", "photo_hover", "accent_color",
]


@admin.route("/team")
@login_required
def team_list():
    members = TeamMember.query.order_by(TeamMember.sort_index, TeamMember.id).all()
    return render_template("admin/team_list.html", members=members)


@admin.route("/team/new", methods=["GET", "POST"])
@login_required
def team_new():
    if request.method == "POST":
        member = TeamMember()
        _apply_team_form(member)
        db.session.add(member)
        db.session.commit()
        flash("Membre créé. Pensez à « Générer le site ».", "ok")
        return redirect(url_for("admin.team_edit", member_id=member.id))
    return render_template("admin/team_form.html", member=None)


@admin.route("/team/<int:member_id>/edit", methods=["GET", "POST"])
@login_required
def team_edit(member_id):
    member = TeamMember.query.get_or_404(member_id)
    if request.method == "POST":
        _apply_team_form(member)
        db.session.commit()
        flash("Modifications enregistrées.", "ok")
        return redirect(url_for("admin.team_edit", member_id=member.id))
    return render_template("admin/team_form.html", member=member)


@admin.route("/team/<int:member_id>/delete", methods=["POST"])
@login_required
def team_delete(member_id):
    member = TeamMember.query.get_or_404(member_id)
    db.session.delete(member)
    db.session.commit()
    flash("Membre supprimé.", "ok")
    return redirect(url_for("admin.team_list"))


# --------------------------------------------------------------------------- #
#  Programmes
# --------------------------------------------------------------------------- #
_PROGRAM_TEXT_FIELDS = [
    "anchor", "category_en", "category_fr", "title_en", "title_fr",
    "where_en", "where_fr", "lead_en", "lead_fr", "points_en", "points_fr",
    "fund_en", "fund_fr", "image", "image_alt_en", "image_alt_fr",
    "link_href", "link_label_en", "link_label_fr",
]


@admin.route("/programs")
@login_required
def program_list():
    programs = Program.query.order_by(Program.sort_index, Program.id).all()
    return render_template("admin/program_list.html", programs=programs)


@admin.route("/programs/new", methods=["GET", "POST"])
@login_required
def program_new():
    if request.method == "POST":
        program = Program()
        _apply_program_form(program)
        db.session.add(program)
        db.session.commit()
        flash("Programme créé. Pensez à « Générer le site ».", "ok")
        return redirect(url_for("admin.program_edit", program_id=program.id))
    return render_template("admin/program_form.html", program=None)


@admin.route("/programs/<int:program_id>/edit", methods=["GET", "POST"])
@login_required
def program_edit(program_id):
    program = Program.query.get_or_404(program_id)
    if request.method == "POST":
        _apply_program_form(program)
        db.session.commit()
        flash("Modifications enregistrées.", "ok")
        return redirect(url_for("admin.program_edit", program_id=program.id))
    return render_template("admin/program_form.html", program=program)


@admin.route("/programs/<int:program_id>/delete", methods=["POST"])
@login_required
def program_delete(program_id):
    program = Program.query.get_or_404(program_id)
    db.session.delete(program)
    db.session.commit()
    flash("Programme supprimé.", "ok")
    return redirect(url_for("admin.program_list"))


# --------------------------------------------------------------------------- #
#  Ressources (publications + vidéos)
# --------------------------------------------------------------------------- #
_RESOURCE_TEXT_FIELDS = [
    "title_en", "title_fr", "subtitle_en", "subtitle_fr",
    "pdf_file", "video_embed", "video_image", "image",
]
_RESOURCE_KINDS = ("publication", "video", "gallery")


@admin.route("/resources")
@login_required
def resource_list():
    resources = Resource.query.order_by(Resource.kind, Resource.sort_index, Resource.id).all()
    return render_template("admin/resource_list.html", resources=resources)


@admin.route("/resources/new", methods=["GET", "POST"])
@login_required
def resource_new():
    if request.method == "POST":
        resource = Resource()
        _apply_resource_form(resource)
        db.session.add(resource)
        db.session.commit()
        flash("Ressource créée. Pensez à « Générer le site ».", "ok")
        return redirect(url_for("admin.resource_edit", resource_id=resource.id))
    return render_template("admin/resource_form.html", resource=None)


@admin.route("/resources/<int:resource_id>/edit", methods=["GET", "POST"])
@login_required
def resource_edit(resource_id):
    resource = Resource.query.get_or_404(resource_id)
    if request.method == "POST":
        _apply_resource_form(resource)
        db.session.commit()
        flash("Modifications enregistrées.", "ok")
        return redirect(url_for("admin.resource_edit", resource_id=resource.id))
    return render_template("admin/resource_form.html", resource=resource)


@admin.route("/resources/<int:resource_id>/delete", methods=["POST"])
@login_required
def resource_delete(resource_id):
    resource = Resource.query.get_or_404(resource_id)
    db.session.delete(resource)
    db.session.commit()
    flash("Ressource supprimée.", "ok")
    return redirect(url_for("admin.resource_list"))


# --------------------------------------------------------------------------- #
#  Comptes (réservé aux admins)
# --------------------------------------------------------------------------- #
@admin.route("/users")
@admin_required
def user_list():
    users = User.query.order_by(User.email).all()
    return render_template("admin/user_list.html", users=users)


@admin.route("/users/new", methods=["POST"])
@admin_required
def user_new():
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    role = "admin" if request.form.get("role") == "admin" else "editor"
    if not email or not password:
        flash("E-mail et mot de passe requis.", "error")
    elif User.query.filter_by(email=email).first():
        flash("Ce compte existe déjà.", "error")
    else:
        user = User(email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash(f"Compte créé : {email} ({role}).", "ok")
    return redirect(url_for("admin.user_list"))


@admin.route("/users/<int:user_id>/delete", methods=["POST"])
@admin_required
def user_delete(user_id):
    if user_id == current_user.id:
        flash("Vous ne pouvez pas supprimer votre propre compte.", "error")
        return redirect(url_for("admin.user_list"))
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("Compte supprimé.", "ok")
    return redirect(url_for("admin.user_list"))


# --------------------------------------------------------------------------- #
#  Publication (génération du site statique)
# --------------------------------------------------------------------------- #
@admin.route("/publish", methods=["POST"])
@login_required
def publish():
    try:
        written = build_site()
        db.session.add(PublishLog(
            user_email=current_user.email, pages_count=len(written),
            status="ok", detail=f"{len(written)} page(s) régénérée(s)."))
        db.session.commit()
        flash(f"Site généré : {len(written)} page(s) mise(s) à jour.", "ok")
    except Exception as exc:  # noqa: BLE001 — on remonte l'erreur à l'utilisateur
        db.session.rollback()
        db.session.add(PublishLog(
            user_email=current_user.email, pages_count=0,
            status="error", detail=str(exc)[:400]))
        db.session.commit()
        flash(f"Échec de la génération : {exc}", "error")
    return redirect(url_for("admin.dashboard"))


@admin.route("/history")
@login_required
def history():
    logs = PublishLog.query.order_by(PublishLog.created_at.desc()).limit(100).all()
    return render_template("admin/history.html", logs=logs)


# --------------------------------------------------------------------------- #
#  Upload d'images
# --------------------------------------------------------------------------- #
@admin.route("/upload", methods=["POST"])
@login_required
def upload():
    file = request.files.get("file")
    if not file or not file.filename:
        return jsonify(error="Aucun fichier reçu."), 400

    ext = Path(file.filename).suffix.lower()
    if ext not in (Config.ALLOWED_IMAGE_EXT | Config.ALLOWED_DOC_EXT):
        return jsonify(error=f"Extension non autorisée ({ext})."), 400

    Config.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    name = _unique_name(secure_filename(file.filename) or f"fichier{ext}")
    dest = Config.UPLOAD_DIR / name
    file.save(dest)

    width = height = None
    if ext in Config.ALLOWED_IMAGE_EXT and ext != ".svg":
        width, height = _optimize_image(dest, ext)

    return jsonify(
        path=f"uploads/{name}",            # valeur à stocker dans Article.image
        url=url_for("media", filename=name),  # aperçu dans l'admin
        width=width, height=height,
    )


# --------------------------------------------------------------------------- #
#  Helpers
# --------------------------------------------------------------------------- #
def _apply_form(article: Article) -> None:
    form = request.form
    for field in _TEXT_FIELDS:
        if field in form:
            setattr(article, field, form.get(field, "").strip())

    # Slug : fourni, sinon dérivé du titre ; toujours normalisé et rendu unique.
    raw_slug = form.get("slug", "").strip() or form.get("title_en", "") or form.get("title_fr", "")
    article.slug = _unique_slug(_slugify(raw_slug), article.id)

    article.managed_detail = form.get("managed_detail") == "on"
    article.status = "published" if form.get("status") == "published" else "draft"
    article.read_minutes = _to_int(form.get("read_minutes"), default=5)
    article.image_w = _to_int(form.get("image_w"), default=1080)
    article.image_h = _to_int(form.get("image_h"), default=720)

    raw_date = form.get("pub_date", "").strip()
    if raw_date:
        try:
            article.pub_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
        except ValueError:
            pass
    article.updated_at = datetime.utcnow()


def _apply_team_form(member: TeamMember) -> None:
    form = request.form
    for field in _TEAM_TEXT_FIELDS:
        if field in form:
            setattr(member, field, form.get(field, "").strip())

    raw_slug = form.get("slug", "").strip() or form.get("name_en", "") or form.get("name_fr", "")
    member.slug = _unique_team_slug(_slugify(raw_slug), member.id)

    member.has_page = form.get("has_page") == "on"
    member.status = "published" if form.get("status") == "published" else "draft"
    member.sort_index = _to_int(form.get("sort_index"), default=0)
    member.photo_w = _to_int(form.get("photo_w"), default=900)
    member.photo_h = _to_int(form.get("photo_h"), default=1350)
    member.photo_hover_w = _to_int(form.get("photo_hover_w"), default=0)
    member.photo_hover_h = _to_int(form.get("photo_hover_h"), default=0)
    if not (member.name_fr or "").strip():
        member.name_fr = member.name_en
    if not (member.role_fr or "").strip():
        member.role_fr = member.role_en


def _unique_team_slug(slug: str, current_id) -> str:
    return _unique_slug_for(TeamMember, slug, current_id)


def _apply_program_form(program: Program) -> None:
    form = request.form
    for field in _PROGRAM_TEXT_FIELDS:
        if field in form:
            setattr(program, field, form.get(field, "").strip())

    raw_slug = form.get("slug", "").strip() or form.get("title_en", "") or form.get("title_fr", "")
    program.slug = _unique_slug_for(Program, _slugify(raw_slug), program.id)

    program.status = "published" if form.get("status") == "published" else "draft"
    program.link_external = form.get("link_external") == "on"
    program.sort_index = _to_int(form.get("sort_index"), default=0)
    program.image_w = _to_int(form.get("image_w"), default=1080)
    program.image_h = _to_int(form.get("image_h"), default=720)


def _apply_resource_form(resource: Resource) -> None:
    form = request.form
    for field in _RESOURCE_TEXT_FIELDS:
        if field in form:
            setattr(resource, field, form.get(field, "").strip())

    kind = form.get("kind")
    resource.kind = kind if kind in _RESOURCE_KINDS else "publication"
    resource.variant = form.get("variant", "") if form.get("variant") in ("", "wide", "tall") else ""
    resource.status = "published" if form.get("status") == "published" else "draft"
    resource.sort_index = _to_int(form.get("sort_index"), default=0)
    resource.video_image_w = _to_int(form.get("video_image_w"), default=1080)
    resource.video_image_h = _to_int(form.get("video_image_h"), default=720)
    resource.image_w = _to_int(form.get("image_w"), default=1600)
    resource.image_h = _to_int(form.get("image_h"), default=1066)


def _unique_slug_for(model, slug: str, current_id) -> str:
    """Garantit l'unicité d'un slug pour un modèle donné (suffixe -2, -3…)."""
    base, i, candidate = slug, 2, slug
    while True:
        existing = model.query.filter_by(slug=candidate).first()
        if existing is None or existing.id == current_id:
            return candidate
        candidate = f"{base}-{i}"
        i += 1


def _to_int(value, default=0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _optimize_image(path: Path, ext: str, max_width: int = 1600):
    """Réduit et recompresse l'image (allège le poids, vise un site rapide).
    Renvoie (largeur, hauteur) finales, ou (None, None) en cas d'échec."""
    try:
        from PIL import Image, ImageOps
        with Image.open(path) as img:
            img = ImageOps.exif_transpose(img)
            if img.width > max_width:
                ratio = max_width / img.width
                img = img.resize((max_width, round(img.height * ratio)))
            size = img.size
            if ext in (".jpg", ".jpeg"):
                img.convert("RGB").save(path, quality=82, optimize=True, progressive=True)
            elif ext == ".webp":
                img.save(path, quality=82, method=6)
            elif ext == ".png":
                img.save(path, optimize=True)
            else:  # .gif et autres : on ne réécrit pas (évite de casser l'animation)
                pass
            return size
    except Exception:  # noqa: BLE001 — l'optimisation est facultative
        return None, None


def _slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text or "article"


def _unique_slug(slug: str, current_id) -> str:
    """Garantit l'unicité du slug (suffixe -2, -3… si nécessaire)."""
    base, i, candidate = slug, 2, slug
    while True:
        existing = Article.query.filter_by(slug=candidate).first()
        if existing is None or existing.id == current_id:
            return candidate
        candidate = f"{base}-{i}"
        i += 1


def _unique_name(name: str) -> str:
    """Évite d'écraser un fichier existant en suffixant -1, -2, …"""
    dest = Config.UPLOAD_DIR / name
    if not dest.exists():
        return name
    stem, ext = Path(name).stem, Path(name).suffix
    i = 1
    while (Config.UPLOAD_DIR / f"{stem}-{i}{ext}").exists():
        i += 1
    return f"{stem}-{i}{ext}"


def register_media_route(app) -> None:
    """Sert les images pour l'aperçu dans l'admin uniquement (hors site public)."""
    @app.route("/media/<path:filename>")
    @login_required
    def media(filename):
        if not Config.UPLOAD_DIR.exists():
            abort(404)
        return send_from_directory(Config.UPLOAD_DIR, filename)

    @app.route("/assets-preview/<path:filename>")
    @login_required
    def asset_preview(filename):
        return send_from_directory(Config.TEMPLATE_DIR / "assets", filename)

    # Sert les images téléversées sous le chemin réel du site (corps d'article,
    # même URL en édition et sur le site publié : /assets/uploads/...).
    @app.route("/assets/uploads/<path:filename>")
    @login_required
    def uploads_asset(filename):
        if not Config.UPLOAD_DIR.exists():
            abort(404)
        return send_from_directory(Config.UPLOAD_DIR, filename)

    # Permet de parcourir le site généré (et les fichiers de prévisualisation)
    # depuis l'admin, avec CSS et images. Les chemins relatifs y résolvent bien.
    @app.route("/admin/preview/<path:filename>")
    @login_required
    def preview_file(filename):
        return send_from_directory(Config.OUTPUT_DIR, filename)
