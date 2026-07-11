"""Modèles de données du CMS.

Chaque contenu stocke ses deux langues côte à côte (champ *_en et *_fr),
fidèle au principe « l'anglais est la source, le français la traduction ».

Phase 1 : seul `Article` est exploité par le générateur (page Actualités).
Les autres modèles (équipe, programmes, ressources, utilisateurs) sont déjà
définis pour préparer les phases suivantes ; ils créent simplement leurs tables.
"""
from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Article(db.Model):
    __tablename__ = "articles"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(160), unique=True, nullable=False)
    # 'draft' = brouillon (non publié), 'published' = en ligne.
    status = db.Column(db.String(16), nullable=False, default="draft")
    pub_date = db.Column(db.Date, nullable=False, default=date.today)

    # True : le CMS génère la page complète de l'article (en/<slug>.html, fr/<slug>.html).
    # False : on conserve une page sur-mesure déjà présente dans template/ (ex. les 3
    # articles d'origine, au design spécifique). On ne l'écrase alors jamais.
    managed_detail = db.Column(db.Boolean, nullable=False, default=True)

    # Carte de la liste des actualités.
    author = db.Column(db.String(120), nullable=False, default="Africa Governance Institute")
    read_minutes = db.Column(db.Integer, nullable=False, default=5)

    image = db.Column(db.String(200), nullable=False, default="")   # ex. "coastal/cf-room.webp"
    image_w = db.Column(db.Integer, nullable=False, default=1080)
    image_h = db.Column(db.Integer, nullable=False, default=720)
    image_alt_en = db.Column(db.String(300), default="")
    image_alt_fr = db.Column(db.String(300), default="")

    category_en = db.Column(db.String(120), default="")
    category_fr = db.Column(db.String(120), default="")
    title_en = db.Column(db.String(300), nullable=False, default="")
    title_fr = db.Column(db.String(300), nullable=False, default="")

    # Phase 2 : page article complète. Présents dès maintenant pour ne pas remigrer.
    body_en = db.Column(db.Text, default="")
    body_fr = db.Column(db.Text, default="")
    meta_description_en = db.Column(db.String(300), default="")
    meta_description_fr = db.Column(db.String(300), default="")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def localized(self, lang: str) -> dict:
        """Renvoie les champs de la carte dans la langue demandée."""
        en = lang == "en"
        return {
            "slug": self.slug,
            "url": f"{self.slug}.html",
            "pub_date": self.pub_date,
            "author": self.author,
            "read_minutes": self.read_minutes,
            "image": self.image,
            "image_w": self.image_w,
            "image_h": self.image_h,
            "alt": self.image_alt_en if en else self.image_alt_fr,
            "category": self.category_en if en else self.category_fr,
            "title": self.title_en if en else self.title_fr,
        }


class TeamMember(db.Model):
    __tablename__ = "team_members"
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(160), unique=True, nullable=False)
    status = db.Column(db.String(16), nullable=False, default="draft")
    sort_index = db.Column(db.Integer, nullable=False, default=0)

    name_en = db.Column(db.String(160), nullable=False, default="")
    name_fr = db.Column(db.String(160), nullable=False, default="")
    role_en = db.Column(db.String(200), default="")
    role_fr = db.Column(db.String(200), default="")
    bio_en = db.Column(db.Text, default="")   # réservé (pages membres bespoke pour l'instant)
    bio_fr = db.Column(db.Text, default="")

    photo = db.Column(db.String(200), default="")
    photo_w = db.Column(db.Integer, default=900)
    photo_h = db.Column(db.Integer, default=1350)
    # Photo affichée au survol (facultative).
    photo_hover = db.Column(db.String(200), default="")
    photo_hover_w = db.Column(db.Integer, default=0)
    photo_hover_h = db.Column(db.Integer, default=0)

    accent_color = db.Column(db.String(16), default="#5E6B27")  # --tint de la carte
    # True : carte cliquable vers team-<slug>.html. False : carte statique (sans page).
    has_page = db.Column(db.Boolean, default=False)

    def localized(self, lang: str) -> dict:
        en = lang == "en"
        name = self.name_en if en else (self.name_fr or self.name_en)
        role = self.role_en if en else (self.role_fr or self.role_en)
        return {
            "slug": self.slug,
            "name": name,
            "role": role,
            "alt": f"{name}, {role}",
            "photo": self.photo,
            "photo_w": self.photo_w,
            "photo_h": self.photo_h,
            "photo_hover": self.photo_hover,
            "photo_hover_w": self.photo_hover_w,
            "photo_hover_h": self.photo_hover_h,
            "accent": self.accent_color,
            "has_page": self.has_page,
        }


class Program(db.Model):
    """Un bloc de la section « initiatives » de programs.html."""
    __tablename__ = "programs"
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(160), unique=True, nullable=False)
    status = db.Column(db.String(16), nullable=False, default="draft")
    sort_index = db.Column(db.Integer, nullable=False, default=0)
    anchor = db.Column(db.String(60), default="")            # id d'ancre HTML (facultatif)

    category_en = db.Column(db.String(160), default="")
    category_fr = db.Column(db.String(160), default="")
    title_en = db.Column(db.String(300), default="")
    title_fr = db.Column(db.String(300), default="")
    where_en = db.Column(db.String(300), default="")        # ligne « lieu · période »
    where_fr = db.Column(db.String(300), default="")
    lead_en = db.Column(db.Text, default="")                # paragraphe de présentation
    lead_fr = db.Column(db.Text, default="")
    points_en = db.Column(db.Text, default="")              # une puce par ligne
    points_fr = db.Column(db.Text, default="")
    fund_en = db.Column(db.String(400), default="")         # « init-fund » (HTML simple autorisé)
    fund_fr = db.Column(db.String(400), default="")

    image = db.Column(db.String(200), default="")
    image_w = db.Column(db.Integer, default=1080)
    image_h = db.Column(db.Integer, default=720)
    image_alt_en = db.Column(db.String(300), default="")
    image_alt_fr = db.Column(db.String(300), default="")

    link_href = db.Column(db.String(300), default="")
    link_label_en = db.Column(db.String(120), default="")
    link_label_fr = db.Column(db.String(120), default="")
    link_external = db.Column(db.Boolean, default=False)

    def localized(self, lang: str) -> dict:
        en = lang == "en"
        pick = lambda a, b: a if en else (b or a)
        raw = self.points_en if en else (self.points_fr or self.points_en)
        points = [p.strip() for p in (raw or "").splitlines() if p.strip()]
        return {
            "anchor": self.anchor,
            "category": pick(self.category_en, self.category_fr),
            "title": pick(self.title_en, self.title_fr),
            "where": pick(self.where_en, self.where_fr),
            "lead": pick(self.lead_en, self.lead_fr),
            "points": points,
            "fund": pick(self.fund_en, self.fund_fr),
            "image": self.image, "image_w": self.image_w, "image_h": self.image_h,
            "alt": pick(self.image_alt_en, self.image_alt_fr),
            "link_href": self.link_href,
            "link_label": pick(self.link_label_en, self.link_label_fr),
            "link_external": self.link_external,
        }


class Resource(db.Model):
    """Une publication (PDF) ou une vidéo de la page ressources."""
    __tablename__ = "resources"
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(16), nullable=False, default="draft")
    sort_index = db.Column(db.Integer, nullable=False, default=0)
    kind = db.Column(db.String(40), default="publication")   # publication | video | gallery

    title_en = db.Column(db.String(300), default="")
    title_fr = db.Column(db.String(300), default="")
    subtitle_en = db.Column(db.String(300), default="")      # « PDF · Rapport… »
    subtitle_fr = db.Column(db.String(300), default="")

    pdf_file = db.Column(db.String(200), default="")         # publication : fichier sous assets/
    video_embed = db.Column(db.String(400), default="")      # vidéo : URL youtube-nocookie/embed
    video_image = db.Column(db.String(200), default="")      # vidéo : image d'aperçu (poster)
    video_image_w = db.Column(db.Integer, default=1080)
    video_image_h = db.Column(db.Integer, default=720)

    # Galerie : image + texte alternatif (title_en/fr) + variante de mise en page.
    image = db.Column(db.String(200), default="")
    image_w = db.Column(db.Integer, default=1600)
    image_h = db.Column(db.Integer, default=1066)
    variant = db.Column(db.String(16), default="")           # '' | 'wide' | 'tall'

    def localized(self, lang: str) -> dict:
        en = lang == "en"
        pick = lambda a, b: a if en else (b or a)
        return {
            "kind": self.kind,
            "title": pick(self.title_en, self.title_fr),
            "subtitle": pick(self.subtitle_en, self.subtitle_fr),
            "pdf_file": self.pdf_file,
            "video_embed": self.video_embed,
            "video_image": self.video_image,
            "video_image_w": self.video_image_w,
            "video_image_h": self.video_image_h,
            "image": self.image,
            "image_w": self.image_w,
            "image_h": self.image_h,
            "variant": self.variant,
        }


class Application(db.Model):
    """Une candidature soumise depuis le formulaire public (Coastal Futures)."""
    __tablename__ = "applications"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default="new")  # new | reviewed | shortlisted | rejected
    lang = db.Column(db.String(2), default="fr")

    # Champs principaux (recherche / affichage rapide).
    nom = db.Column(db.String(160), default="")
    prenom = db.Column(db.String(160), default="")
    email = db.Column(db.String(190), default="")
    telephone = db.Column(db.String(60), default="")
    date_naissance = db.Column(db.String(40), default="")
    genre = db.Column(db.String(40), default="")
    nationalite = db.Column(db.String(120), default="")
    pays_residence = db.Column(db.String(120), default="")
    ville = db.Column(db.String(120), default="")
    tranche_age = db.Column(db.String(40), default="")
    profession = db.Column(db.String(200), default="")
    organisation = db.Column(db.String(200), default="")
    langues = db.Column(db.String(200), default="")
    statut = db.Column(db.String(400), default="")      # cases multiples, jointes par « ; »
    domaines = db.Column(db.String(400), default="")    # cases multiples, jointes par « ; »
    motivation = db.Column(db.Text, default="")
    experience = db.Column(db.Text, default="")
    contribution = db.Column(db.Text, default="")

    # Toutes les réponses brutes (robuste aux évolutions du formulaire).
    data_json = db.Column(db.Text, default="")

    # Pièces jointes : chemin relatif sous APPLICATIONS_DIR (privé, hors public_html).
    cv_file = db.Column(db.String(300), default="")
    lettre_file = db.Column(db.String(300), default="")
    identite_file = db.Column(db.String(300), default="")
    projet_file = db.Column(db.String(300), default="")

    def full_name(self):
        return f"{self.prenom} {self.nom}".strip() or self.email or f"Candidature #{self.id}"

    def files(self):
        """Renvoie [(label, champ, chemin), …] pour les pièces présentes."""
        mapping = [("CV", "cv_file"), ("Lettre de motivation", "lettre_file"),
                   ("Pièce d'identité", "identite_file"), ("Projet", "projet_file")]
        return [(label, field, getattr(self, field)) for label, field in mapping if getattr(self, field)]


class PublishLog(db.Model):
    """Une entrée de l'historique : chaque génération du site (« Publier »)."""
    __tablename__ = "publish_log"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_email = db.Column(db.String(190), default="")
    pages_count = db.Column(db.Integer, default=0)
    status = db.Column(db.String(16), default="ok")          # ok | error
    detail = db.Column(db.String(400), default="")           # résumé / message d'erreur


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(190), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="editor")  # editor | admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)
