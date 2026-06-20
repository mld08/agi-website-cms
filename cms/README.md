# AGI CMS — Phase 1

Mini-CMS pour le site de l'Africa Governance Institute. L'administration tourne
en **Flask + base de données** ; le site public est **généré en HTML statique**
(rapide, robuste, SEO préservé). Si Python s'arrête, le site public reste en ligne.

## Principe

```
ADMIN (Flask + base)  ──build──▶  public/  (HTML statique servi par Apache)
   contenu éditable                en/news.html  ·  fr/news.html  ·  assets…
```

Le contenu éditable (les articles) vit dans la base. Le reste du site (design,
CSS, JS, images, pages non encore migrées) provient de `../template/` et est
recopié tel quel à chaque génération, pour garder un site complet.

## Arborescence

```
cms/
  app.py            Application Flask + commandes CLI
  config.py         Configuration (base de données, URL du site, sortie)
  models.py         Tables : articles, équipe, programmes, ressources, utilisateurs
  locales.py        Libellés du gabarit par langue (EN/FR) + mois localisés
  generator.py      Générateur statique (base → public/)
  seed.py           Les 3 articles existants (données de départ)
  schema.sql        Schéma MySQL de référence (pour phpMyAdmin / cPanel)
  passenger_wsgi.py Point d'entrée cPanel
  admin.py          Tableau de bord d'administration (Phase 2/3)
  templates/
    base.html          Gabarit commun (barre utilitaire, en-tête, pied de page)
    news_list.html     Page Actualités (liste)
    article_detail.html Page d'article complète (générée depuis le WYSIWYG)
    team_grid.html     Grille de l'équipe (injectée dans about.html)
    programs_initiatives.html  Programmes (injectés dans programs.html)
    resources_publications.html / resources_videos.html / resources_gallery.html  (injectés dans resources.html)
    admin/             Gabarits de l'administration (connexion, listes, formulaires)
```

## Démarrage en local (Windows)

En local, aucune base MySQL n'est nécessaire : on utilise SQLite automatiquement.

```powershell
cd cms
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# Tout en un : crée les tables, insère les articles, génère le site
.\.venv\Scripts\flask.exe --app app rebuild
```

Le site est généré dans `../public/`. Ouvrez `../public/en/news.html` ou
`../public/fr/news.html` dans un navigateur pour vérifier.

Pour lancer l'admin (placeholder en Phase 1) :

```powershell
.\.venv\Scripts\flask.exe --app app run
```

### Commandes disponibles

| Commande | Rôle |
|---|---|
| `flask --app app init-db` | Crée les tables |
| `flask --app app seed`    | Insère les 3 articles existants |
| `flask --app app create-user EMAIL MOTDEPASSE` | Crée un compte admin |
| `flask --app app build`   | Génère le site statique dans `OUTPUT_DIR` |
| `flask --app app rebuild` | init-db + seed + build, d'un coup |

## Administration (Phase 2)

Interface en français pour gérer les articles, sans toucher au code.

```powershell
# 1. Créer un compte (une seule fois)
.\.venv\Scripts\flask.exe --app app create-user "vous@exemple.com" "VotreMotDePasse"

# 2. Lancer l'admin
.\.venv\Scripts\flask.exe --app app run
```

Ouvrez **http://127.0.0.1:5000/admin** et connectez-vous. Vous pouvez :

- créer / modifier / supprimer un article (titre, catégorie, date, auteur…) en
  **français et anglais côte à côte** ;
- rédiger le corps avec un **éditeur visuel** (gras, titres, listes, liens) ;
- **téléverser une image** : ses dimensions sont détectées automatiquement ;
- basculer un article entre **Brouillon** et **Publié** ;
- cliquer sur **Générer le site** pour régénérer le HTML public.

Flux de travail : on rédige → on passe en « Publié » → on clique **Générer le
site**. Tant qu'on n'a pas généré, le site public ne change pas.

## Déploiement sur cPanel (aperçu)

1. **Base MySQL** : créez une base + un utilisateur dans cPanel, notez les
   identifiants.
2. **Fichier `.env`** : copiez `.env.example` en `.env` et renseignez
   `SECRET_KEY`, `DATABASE_URL` (MySQL) et `SITE_URL`.
3. **Setup Python App** : pointez l'application sur le dossier `cms/`, lancez
   `pip install -r requirements.txt`, puis `flask --app app rebuild`.
4. **Site public** : faites pointer `OUTPUT_DIR` sur `public_html` (ou copiez-y
   le contenu de `public/`). Le `.htaccess` existant reste valable.
5. Après chaque mise à jour, relancez `build` et cliquez **Restart** dans
   « Setup Python App ».

## Notes de fidélité

- Les pages générées reproduisent le HTML d'origine. Jinja échappe automatiquement
  le contenu (sécurité), donc les apostrophes peuvent apparaître en `&#39;` et les
  esperluettes en `&amp;` : c'est strictement équivalent à l'affichage et plus sûr
  pour du contenu saisi par l'équipe.
- Le SEO (canonical, hreflang, JSON-LD, Open Graph) est régénéré par les gabarits :
  impossible de l'oublier en ajoutant un article.

## Pages d'article complètes (Phase 3)

Chaque article publié génère sa page complète **EN + FR** (`en/<slug>.html`,
`fr/<slug>.html`) depuis le corps WYSIWYG, avec SEO dédié (canonical, hreflang,
Open Graph `article`, JSON-LD `NewsArticle`).

- **Pages sur-mesure préservées.** Les 3 articles d'origine ont un design
  spécifique : ils sont marqués « page non générée » (`managed_detail = False`)
  et **ne sont jamais écrasés**. Décochez « Générer automatiquement la page de
  l'article » pour tout article qui possède déjà une page sur-mesure.
- **Slug automatique.** Laissez le champ vide : il est dérivé du titre, normalisé
  et rendu unique.
- **Images optimisées.** À l'upload, les images sont redimensionnées (max 1600 px
  de large) et recompressées pour un site rapide.
- **Pruning sûr.** Si un article est supprimé ou renommé, son ancienne page est
  retirée du site au build suivant (via un manifeste stocké dans `instance/`),
  sans jamais toucher aux pages sur-mesure ni au reste du template.

> Note dev : après un changement de schéma (ex. ajout de `managed_detail`),
> supprimez `instance/cms.db` puis relancez `rebuild` en local. En production
> MySQL, ajoutez la colonne (voir `schema.sql`) ou recréez la table.

## Équipe (Phase 4)

La grille de l'équipe sur **about.html** (EN + FR) est entièrement éditable depuis
l'admin (menu **Équipe**) : ajout, modification, suppression, réordonnancement,
rôles bilingues, couleur d'accent, photo + photo au survol.

- **Injection ciblée.** Seule la grille est régénérée, entre les marqueurs
  `<!-- CMS:TEAM_GRID --> … <!-- /CMS:TEAM_GRID -->` présents dans `about.html`.
  Tout le reste de la page (introduction, mission, CTA…) reste tel quel.
- **Cartes liées ou statiques.** « Carte cliquable » renvoie vers une page
  `team-<slug>.html` ; sinon la carte est statique (sans page). Les **pages
  membres détaillées restent sur-mesure** (designs très spécifiques) : le CMS ne
  les génère pas, il gère la grille.
- **Numérotation automatique** (01, 02, …) selon l'ordre d'affichage.

> Note dev : le modèle équipe a de nouvelles colonnes. En local, supprimez
> `instance/cms.db` puis `rebuild`. En prod MySQL, ajoutez les colonnes
> (voir `schema.sql`) ou recréez la table `team_members`.

## Programmes & Ressources (Phase 5)

Même mécanique d'injection ciblée que l'équipe, étendue à deux pages :

- **Programmes** (menu **Programmes**) : la section « initiatives » de
  `programs.html` (EN + FR) est éditable (titre, catégorie, lieu/période,
  présentation, puces, financement, image, lien interne ou externe, ordre).
  Zone `<!-- CMS:PROGRAMS --> … <!-- /CMS:PROGRAMS -->`.
- **Ressources** (menu **Ressources**) : les **publications (PDF)** et les
  **vidéos** de `resources.html` / `ressources.html` sont éditables. Zones
  `<!-- CMS:RESOURCES_PUBS -->` et `<!-- CMS:RESOURCES_VIDEOS -->`. L'upload
  accepte désormais les **PDF** (copiés dans `assets/uploads`). La galerie photo
  et l'en-tête restent sur-mesure.

> Note dev : nouvelles colonnes sur `programs` et `resources`. En local,
> supprimez `instance/cms.db` puis `rebuild`. En prod MySQL, recréez ces tables
> (voir `schema.sql`).

## Confort (Phase 6)

- **Images dans le corps des articles.** Le bouton image de l'éditeur téléverse
  et insère l'image (URL `/assets/uploads/…`, identique en édition et sur le site
  publié). Une règle `.prose img` les cadre proprement.
- **Prévisualisation avant publication.** Sur un article, « Prévisualiser (FR/EN) »
  ouvre la page rendue (même un brouillon) sans la publier. Le menu **Voir le
  site ↗** permet de parcourir le site généré (CSS, images compris) depuis l'admin,
  via `/admin/preview/…`. Les fichiers d'aperçu temporaires sont nettoyés à chaque
  génération.
- **Rôles éditeur / admin.** Un **éditeur** gère tout le contenu (articles, équipe,
  programmes, ressources) et publie. Un **admin** peut en plus gérer les **comptes**
  (menu **Comptes**, réservé aux admins). Création de comptes via l'admin ou la
  commande `create-user --role admin|editor`.

## Design de l'administration

L'admin respecte la **charte graphique du site** : polices **Poppins** (texte) et
**Cormorant Garamond** (grands titres), couleurs de marque (rouge, olive, orange,
jaune), surfaces crème/encre, logo et bande quadrichrome. Tout est dans
`static/admin.css` (qui rebrande Bootstrap via ses variables `--bs-*`) et les
polices/logo dans `static/`. La page de connexion a un fond sombre dédié.

Aperçu local de l'admin (sans Bash, via la config `.claude/launch.json`) : un
serveur de prévisualisation est défini sous le nom `cms`.

## Galerie & Historique (Phase 6.5)

- **Galerie photo** : les photos de la page Ressources sont gérées depuis l'admin
  (menu **Ressources**, type « Galerie »). Chaque photo a une image, un texte
  alternatif bilingue, des dimensions et une mise en page (normale / large / haute).
  Zone `<!-- CMS:RESOURCES_GALLERY -->`. La visionneuse (lightbox) reste assurée
  par le JS existant.
- **Historique des publications** : chaque « Générer le site » est journalisé
  (date UTC, auteur, nombre de pages, succès/erreur). Consultable via le menu
  **Historique** (table `publish_log`).

> Note dev : nouvelles colonnes sur `resources` + nouvelle table `publish_log`.
> En local, supprimez `instance/cms.db` puis `rebuild`. En prod MySQL, recréez
> `resources` et créez `publish_log` (voir `schema.sql`).

## Prochaines étapes possibles

- Déploiement automatisé vers cPanel.
- Bloc « featured » de la page Ressources géré depuis l'admin (optionnel).


.\.venv\Scripts\flask.exe --app app create-user "ton@email.com" "motdepasse"