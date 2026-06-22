# Déploiement sur cPanel

Topologie cible :

```
africagovernanceinstitute.org          → public_html/         (site public statique)
cms.africagovernanceinstitute.org      → app Python Flask     (administration)
```

Arborescence sur le serveur (remplacez `COMPTE` par votre identifiant cPanel) :

```
/home/COMPTE/
├── public_html/                       ← site généré (OUTPUT_DIR) — domaine principal
├── template/                          ← design source (en/, fr/, assets/, css, js)  (TEMPLATE_DIR)
└── cms.africagovernanceinstitute.org/ ← app Flask (racine de l'app Python + docroot du sous-domaine)
    ├── app.py, config.py, models.py, admin.py, generator.py, seed.py, locales.py
    ├── passenger_wsgi.py
    ├── requirements.txt
    ├── .env                            ← à créer (voir étape 5)
    ├── templates/  static/  uploads/
    └── instance/                       ← créé automatiquement (manifeste de build)
```

Principe : l'admin (sous-domaine) écrit le site généré **directement dans `public_html`**.
`public_html` est donc **entièrement géré** par le CMS (source de vérité = `template/` + base).

---

## 1. Base de données MySQL

cPanel → **MySQL® Databases** :

1. **Créer une base** : nom `agicms` → devient `COMPTE_agicms`.
2. **Créer un utilisateur** : nom `agicms` → devient `COMPTE_agicms`, avec un mot de passe fort.
3. **Ajouter l'utilisateur à la base** avec **ALL PRIVILEGES**.

Notez : base `COMPTE_agicms`, utilisateur `COMPTE_agicms`, mot de passe, hôte `localhost`.

## 2. Sous-domaine

cPanel → **Domains** (ou **Subdomains**) → créer `cms.africagovernanceinstitute.org`.
Document Root proposé : `/home/COMPTE/cms.africagovernanceinstitute.org` (gardez ce nom).

## 3. Application Python (Passenger)

cPanel → **Setup Python App** → **Create Application** :

- **Python version** : 3.10+ (la plus récente disponible).
- **Application root** : `cms.africagovernanceinstitute.org`
- **Application URL** : `cms.africagovernanceinstitute.org`
- **Application startup file** : `passenger_wsgi.py`
- **Application Entry point** : `application`

Créez. cPanel crée un virtualenv et affiche en haut une commande
`source /home/COMPTE/virtualenv/.../bin/activate && cd ...` — **copiez-la**, elle sert
à l'étape 6.

## 4. Téléverser les fichiers

- Le contenu du dossier local **`cms/`** → dans `/home/COMPTE/cms.africagovernanceinstitute.org/`
  (app.py, config.py, …, `templates/`, `static/`, `passenger_wsgi.py`, `requirements.txt`).
  N'envoyez PAS `.venv/`, `instance/`, ni `.env` local.
- Le dossier local **`template/`** → dans `/home/COMPTE/template/`.

(via le Gestionnaire de fichiers cPanel en .zip puis « Extract », ou via Git/SFTP.)

## 5. Fichier `.env`

Dans `/home/COMPTE/cms.africagovernanceinstitute.org/`, créez `.env` (Gestionnaire de
fichiers → New File → `.env` → Edit). **Sans terminal**, on installe via la page web
`/setup` : renseignez donc aussi `SETUP_TOKEN` + `ADMIN_EMAIL` + `ADMIN_PASSWORD`.

```
SECRET_KEY=<longue chaîne aléatoire>
DATABASE_URL=mysql+pymysql://COMPTE_agicms:MOTDEPASSE@localhost/COMPTE_agicms?charset=utf8mb4
SITE_URL=https://africagovernanceinstitute.org
OUTPUT_DIR=/home/COMPTE/public_html
TEMPLATE_DIR=/home/COMPTE/template

SETUP_TOKEN=un-long-jeton-secret-aleatoire
ADMIN_EMAIL=vous@exemple.com
ADMIN_PASSWORD=UnMotDePasseFort
```

(Pour `SECRET_KEY` et `SETUP_TOKEN`, mettez de longues chaînes aléatoires, p. ex.
depuis https://www.random.org/strings/ ou un gestionnaire de mots de passe.)

## 6. Installer les dépendances (sans terminal)

Sur la page **Setup Python App** de votre application :

1. Section **Configuration files** : saisissez `requirements.txt` puis **Add**.
2. Cliquez **Run Pip Install**. Attendez la fin (les paquets s'installent dans le venv).
3. Cliquez **Restart** (bouton en haut) pour recharger l'app avec ses dépendances.

## 7. Initialiser via la page web `/setup` (sans terminal)

L'app inclut une page d'installation à usage unique, protégée par `SETUP_TOKEN`.

1. Ouvrez : `https://cms.africagovernanceinstitute.org/setup/VOTRE_SETUP_TOKEN`
2. Elle crée les tables MySQL, insère le contenu existant, crée votre compte admin
   (depuis `ADMIN_EMAIL` / `ADMIN_PASSWORD`) et génère le site dans `public_html`.
   Un résumé s'affiche (ou l'erreur exacte à corriger).
3. **Sécurisez ensuite** : dans `.env`, videz `SETUP_TOKEN=` (et idéalement
   `ADMIN_PASSWORD=`), puis **Restart**. La page `/setup` renverra alors 404.

> Variante phpMyAdmin (facultatif) : vous pouvez aussi créer les tables en important
> `schema.sql` dans phpMyAdmin ; mais la page `/setup` fait tout, c'est plus simple.

## 8. HTTPS

cPanel → **SSL/TLS Status** → cochez `cms.africagovernanceinstitute.org` → **Run AutoSSL**
(le domaine principal a déjà son certificat). Le `.htaccess` du site force déjà HTTPS côté public.

## 9. Vérifier

- `https://cms.africagovernanceinstitute.org/admin` → page de connexion brandée.
- Connectez-vous, modifiez un contenu, cliquez **Générer le site**.
- `https://africagovernanceinstitute.org` → le site public reflète les changements.

---

## Mettre à jour le CONTENU (usage courant)

Aucune manipulation technique : se connecter à l'admin → éditer → **Générer le site**.
Le site public est mis à jour immédiatement (l'historique journalise chaque génération).

## Mettre à jour le CODE du CMS

Après avoir remplacé des fichiers `.py`/templates :

```bash
mkdir -p /home/COMPTE/cms.africagovernanceinstitute.org/tmp
touch /home/COMPTE/cms.africagovernanceinstitute.org/tmp/restart.txt
```

(ou bouton **Restart** dans Setup Python App). Si le **schéma** de la base a changé :
réactivez temporairement `SETUP_TOKEN` dans `.env`, Restart, ouvrez de nouveau
`/setup/<token>` (crée les **nouvelles tables** manquantes), puis revidez `SETUP_TOKEN`.
Pour modifier des **colonnes existantes**, passez par **phpMyAdmin** (voir `schema.sql`).

## Dépannage

- **Erreur 500 / page blanche** : consultez `stderr.log` dans le dossier de l'app, ou
  les logs Passenger. Vérifiez `.env` (DATABASE_URL) et que `pip install` a réussi.
- **Accents cassés en base** : vérifiez `?charset=utf8mb4` dans `DATABASE_URL`.
- **Le CSS/police de l'admin ne charge pas** : Flask sert `/static/` lui-même ; vérifiez
  que `static/` a bien été téléversé. (Aucune config Apache nécessaire.)
- **Permission denied en écrivant public_html** : l'app tourne sous votre compte, elle a
  les droits ; vérifiez que `OUTPUT_DIR` pointe bien sur `/home/COMPTE/public_html`.
- **« Générer » ne change rien** : vérifiez `TEMPLATE_DIR` (doit pointer sur `/home/COMPTE/template`).
