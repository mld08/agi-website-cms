"""Générateur de site statique.

Lit le contenu publié dans la base, copie le site d'origine (template/) vers le
dossier de sortie, puis écrase les pages gérées par le CMS avec des versions
générées depuis les gabarits Jinja. Le site public reste ainsi du HTML pur :
si l'application Python s'arrête, les visiteurs ne voient aucune différence.
"""
import json
import re
import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from config import Config, BASE_DIR
from models import Article, TeamMember, Program, Resource
from locales import LOCALES, MONTHS, MONTHS_FULL, COPYRIGHT

# Fichier ressources par langue (le nom diffère en FR) + libellés localisés.
RES_FILE = {"en": "resources.html", "fr": "ressources.html"}
RES_LABELS = {
    "en": {"download": "Download", "play": "Play the video:"},
    "fr": {"download": "Télécharger", "play": "Lire la vidéo :"},
}


def _replace_region(page: Path, marker: str, html: str) -> bool:
    """Remplace la zone entre <!-- CMS:MARKER --> et <!-- /CMS:MARKER --> par `html`.
    Renvoie True si la zone a été trouvée et remplacée."""
    if not page.exists():
        return False
    rx = re.compile(rf"<!-- CMS:{marker} -->.*?<!-- /CMS:{marker} -->", re.S)
    replacement = f"<!-- CMS:{marker} -->\n{html}\n    <!-- /CMS:{marker} -->"
    # Lambda : renvoie le remplacement littéral (évite l'interprétation des \1, etc.).
    new_html, n = rx.subn(lambda _m: replacement, page.read_text(encoding="utf-8"), count=1)
    if n:
        page.write_text(new_html, encoding="utf-8")
    return bool(n)

LANGS = ("en", "fr")
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
# Liste des pages écrites par le CMS au build précédent : sert à supprimer les
# pages devenues orphelines (article supprimé, renommé, ou repassé en sur-mesure).
# Stockée hors du site public (dans instance/) pour ne pas l'exposer.
MANIFEST_PATH = BASE_DIR / "instance" / "build_manifest.json"

# Fichiers de travail à ne jamais publier (déjà bloqués aussi par le .htaccess).
_IGNORE = shutil.ignore_patterns("*.md", ".thumbnail")


def _env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
    )


def _copy_template(out_dir: Path) -> None:
    """Copie le site d'origine (assets, CSS, JS, pages non encore migrées)."""
    shutil.copytree(Config.TEMPLATE_DIR, out_dir, dirs_exist_ok=True, ignore=_IGNORE)


def _prune_previous(out_dir: Path) -> None:
    """Supprime les pages générées au build précédent (avant de tout régénérer).
    Ne touche qu'aux fichiers que LE CMS a écrits : les pages sur-mesure et le
    reste du template sont restaurés juste après par la copie du template."""
    try:
        previous = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError):
        return
    for rel in previous:
        target = out_dir / rel
        try:
            if target.is_file():
                target.unlink()
        except OSError:
            pass


def _save_manifest(written: list) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(written), encoding="utf-8")


def _copy_uploads(out_dir: Path) -> None:
    """Copie les images téléversées depuis l'admin vers public/assets/uploads."""
    src = Config.UPLOAD_DIR
    if src.exists():
        dst = out_dir / "assets" / "uploads"
        shutil.copytree(src, dst, dirs_exist_ok=True)


def _card(article: Article, lang: str) -> dict:
    data = article.localized(lang)
    d = data["pub_date"]
    data["day"] = f"{d.day:02d}"
    data["mon"] = MONTHS[lang][d.month]
    return data


def _long_date(d, lang: str) -> str:
    return f"{d.day} {MONTHS_FULL[lang][d.month]} {d.year}"


def _detail(article: Article, lang: str) -> dict:
    en = lang == "en"
    return {
        "slug": article.slug,
        "title": article.title_en if en else article.title_fr,
        "category": article.category_en if en else article.category_fr,
        "author": article.author,
        "read_minutes": article.read_minutes,
        "deck": article.meta_description_en if en else article.meta_description_fr,
        "body": article.body_en if en else article.body_fr,
        "image": article.image,
        "image_w": article.image_w,
        "image_h": article.image_h,
        "alt": article.image_alt_en if en else article.image_alt_fr,
        "iso_date": article.pub_date.isoformat(),
        "long_date": _long_date(article.pub_date, lang),
    }


def _detail_context(article: Article, lang: str) -> dict:
    site = Config.SITE_URL
    slug = article.slug
    return {
        "lang": lang,
        "t": LOCALES[lang],
        "copyright": COPYRIGHT,
        "a": _detail(article, lang),
        "home_label": LOCALES[lang]["news"]["crumb_home"],
        "news_label": LOCALES[lang]["news"]["crumb_now"],
        "alt_en": f"../en/{slug}.html",
        "alt_fr": f"../fr/{slug}.html",
        "canonical": f"{site}/{lang}/{slug}.html",
        "alt_en_abs": f"{site}/en/{slug}.html",
        "alt_fr_abs": f"{site}/fr/{slug}.html",
        "og_image": f"{site}/assets/{article.image}" if article.image else "",
    }


def _inject_team(out_dir: Path, env: Environment) -> list:
    """Régénère la grille de l'équipe dans about.html (EN + FR) entre les marqueurs."""
    members = (
        TeamMember.query.filter_by(status="published")
        .order_by(TeamMember.sort_index, TeamMember.id).all()
    )
    tpl = env.get_template("team_grid.html")
    written = []
    for lang in LANGS:
        page = out_dir / lang / "about.html"
        if _replace_region(page, "TEAM_GRID", tpl.render(members=[m.localized(lang) for m in members])):
            written.append(str(page.relative_to(out_dir)))
    return written


def _inject_programs(out_dir: Path, env: Environment) -> list:
    """Régénère la section « initiatives » dans programs.html (EN + FR)."""
    programs = (
        Program.query.filter_by(status="published")
        .order_by(Program.sort_index, Program.id).all()
    )
    tpl = env.get_template("programs_initiatives.html")
    written = []
    for lang in LANGS:
        page = out_dir / lang / "programs.html"
        if _replace_region(page, "PROGRAMS", tpl.render(programs=[p.localized(lang) for p in programs])):
            written.append(str(page.relative_to(out_dir)))
    return written


def _inject_resources(out_dir: Path, env: Environment) -> list:
    """Régénère les publications et les vidéos dans resources.html / ressources.html."""
    def by_kind(kind):
        return (
            Resource.query.filter_by(status="published", kind=kind)
            .order_by(Resource.sort_index, Resource.id).all()
        )
    pubs, videos, gallery = by_kind("publication"), by_kind("video"), by_kind("gallery")
    pub_tpl = env.get_template("resources_publications.html")
    vid_tpl = env.get_template("resources_videos.html")
    gal_tpl = env.get_template("resources_gallery.html")
    written = []
    for lang in LANGS:
        page = out_dir / lang / RES_FILE[lang]
        labels = RES_LABELS[lang]
        changed = [
            _replace_region(page, "RESOURCES_PUBS",
                            pub_tpl.render(items=[r.localized(lang) for r in pubs], download_label=labels["download"])),
            _replace_region(page, "RESOURCES_VIDEOS",
                            vid_tpl.render(items=[r.localized(lang) for r in videos], play_label=labels["play"])),
            _replace_region(page, "RESOURCES_GALLERY",
                            gal_tpl.render(items=[r.localized(lang) for r in gallery])),
        ]
        if any(changed):
            written.append(str(page.relative_to(out_dir)))
    return written


def _news_context(lang: str, articles) -> dict:
    site = Config.SITE_URL
    return {
        "lang": lang,
        "t": LOCALES[lang],
        "news": LOCALES[lang]["news"],
        "copyright": COPYRIGHT,
        # Liens du sélecteur de langue (relatifs, dans la page).
        "alt_en": "../en/news.html",
        "alt_fr": "../fr/news.html",
        # URLs absolues pour le SEO.
        "canonical": f"{site}/{lang}/news.html",
        "alt_en_abs": f"{site}/en/news.html",
        "alt_fr_abs": f"{site}/fr/news.html",
        "home_url": f"{site}/{lang}/",
        "og_image": f"{site}/assets/coastal/cf-room.webp",
        "articles": [_card(a, lang) for a in articles],
    }


def render_detail(article: Article, lang: str) -> str:
    """Rend la page d'un article en HTML (utilisé pour la prévisualisation)."""
    return _env().get_template("article_detail.html").render(**_detail_context(article, lang))


def build_site() -> list[str]:
    """Génère le site complet dans Config.OUTPUT_DIR. Renvoie la liste des
    pages écrites par le CMS."""
    out_dir = Config.OUTPUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    # 0) Nettoyer les pages générées au build précédent (supprime les orphelines)
    #    et les fichiers de prévisualisation temporaires.
    _prune_previous(out_dir)
    for lang in LANGS:
        preview = out_dir / lang / "_preview.html"
        if preview.exists():
            preview.unlink()

    # 1) Repartir du site d'origine pour garder un site complet à chaque build.
    _copy_template(out_dir)
    _copy_uploads(out_dir)

    # 2) Régénérer les pages gérées par le CMS.
    env = _env()
    news_tpl = env.get_template("news_list.html")
    detail_tpl = env.get_template("article_detail.html")

    articles = (
        Article.query
        .filter_by(status="published")
        .order_by(Article.pub_date.desc(), Article.id.desc())
        .all()
    )

    written = []

    # 2a) Liste des actualités (EN + FR).
    for lang in LANGS:
        html = news_tpl.render(**_news_context(lang, articles))
        target = out_dir / lang / "news.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(html, encoding="utf-8")
        written.append(str(target.relative_to(out_dir)))

    # 2b) Pages d'article complètes, uniquement pour les articles gérés par le CMS.
    #     Les articles à page sur-mesure (managed_detail = False) ne sont jamais écrasés.
    for article in articles:
        if not article.managed_detail:
            continue
        for lang in LANGS:
            html = detail_tpl.render(**_detail_context(article, lang))
            target = out_dir / lang / f"{article.slug}.html"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(html, encoding="utf-8")
            written.append(str(target.relative_to(out_dir)))

    # 2c) Sections injectées dans les pages existantes (entre marqueurs).
    written.extend(_inject_team(out_dir, env))         # about.html
    written.extend(_inject_programs(out_dir, env))     # programs.html
    written.extend(_inject_resources(out_dir, env))    # resources.html / ressources.html

    _save_manifest(written)
    return written
