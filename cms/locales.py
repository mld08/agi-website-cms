"""Textes d'interface par langue (le « chrome » du site) + contenu de la page
Actualités. Ces chaînes ne sont PAS du contenu éditable par l'équipe : ce sont
les libellés fixes du gabarit (navigation, pied de page…). Le contenu éditable
(articles) vient de la base de données.

Le HTML stocké ici est de confiance (écrit par nous), il est rendu tel quel.
"""

# Abréviations de mois, fidèles au site existant (FR : « juin », « mai », « sept. »…).
MONTHS = {
    "en": ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
           "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "fr": ["", "janv.", "févr.", "mars", "avr.", "mai", "juin",
           "juil.", "août", "sept.", "oct.", "nov.", "déc."],
}

# Mois en toutes lettres, pour la date longue des pages d'article (« 20 September 2023 »).
MONTHS_FULL = {
    "en": ["", "January", "February", "March", "April", "May", "June",
           "July", "August", "September", "October", "November", "December"],
    "fr": ["", "janvier", "février", "mars", "avril", "mai", "juin",
           "juillet", "août", "septembre", "octobre", "novembre", "décembre"],
}

COPYRIGHT = "© 2026 Africa Governance Institute · Institut Africain de la Gouvernance"

LOCALES = {
    "en": {
        "skip": "Skip to main content",
        "location": "Dakar, Senegal",
        "lang_code": "EN",
        "socials_label": "Social links",
        # Navigation principale : (libellé, href dans l'arbre /en/)
        "nav": [
            ("Who We Are", "about.html"),
            ("News", "news.html"),
            ("Our Programs", "programs.html"),
            ("Resources", "resources.html"),
        ],
        "contact": "Contact",
        # Pied de page
        "footer_blurb": "A pan-African think tank of excellence committed to "
                        "transforming public institutions and promoting innovative, "
                        "inclusive and sustainable governance.",
        "quick_links_h": "Quick Links",
        "quick_links": [
            ("About Us", "about.html"),
            ("Our Programs", "programs.html"),
            ("Resources", "resources.html"),
            ("News & Articles", "news.html"),
            ("Initiatives", "index.html#initiatives"),
            ("Contact", "contact.html"),
        ],
        "newsletter_h": "Newsletter",
        "newsletter_text_html": 'Subscribe for the latest in your inbox, once a month. '
                                'By subscribing, you agree to our '
                                '<a href="privacy-policy.html" style="text-decoration:underline">privacy policy</a>.',
        "newsletter_label": "Email address",
        "newsletter_placeholder": "Enter your email address",
        "newsletter_button": "Join",
        "legal_links": [
            ("Legal notice", "legal-notice.html"),
            ("Privacy policy", "privacy-policy.html"),
            ("Accessibility", "accessibility.html"),
            ("Sitemap", "sitemap.html"),
        ],
        # Cartes d'article
        "by": "By",
        "read_suffix": "min read",
        # Page Actualités (en-tête + SEO + bloc « plus »)
        "news": {
            "title": "News & Analysis · Africa Governance Institute",
            "description": "News, reports and analysis from the Africa Governance "
                           "Institute on the governance and economic questions shaping the continent.",
            "author_meta": "Africa Governance Institute",
            "og_title": "News & Analysis · Africa Governance Institute",
            "og_description": "Reports and analysis from the Africa Governance Institute.",
            "og_image_alt": "News & Analysis",
            "crumb_home": "Home",
            "crumb_now": "News",
            "eyebrow": "Newsroom",
            "h1": "News & Analysis",
            "deck": "Reports and analysis from the Africa Governance Institute on the "
                    "governance and economic questions shaping the continent.",
            "more_h2": "New analysis is added here through the year.",
            "more_p": "Reports are published as our research and events conclude, with "
                      "the most recent shown first. Subscribe to be notified when the next one is out.",
            "more_link": "Subscribe for updates",
        },
    },
    "fr": {
        "skip": "Aller au contenu principal",
        "location": "Dakar, Sénégal",
        "lang_code": "FR",
        "socials_label": "Réseaux sociaux",
        "nav": [
            ("Qui sommes-nous", "about.html"),
            ("Actualités", "news.html"),
            ("Nos Programmes", "programs.html"),
            ("Ressources", "ressources.html"),
        ],
        "contact": "Contact",
        "footer_blurb": "Think Tank panafricain d’excellence engagé dans la transformation "
                        "des institutions publiques et la promotion d’une gouvernance "
                        "innovante, inclusive et durable.",
        "quick_links_h": "Liens rapides",
        "quick_links": [
            ("À propos", "about.html"),
            ("Nos Programmes", "programs.html"),
            ("Ressources", "ressources.html"),
            ("Actualités & Articles", "news.html"),
            ("Initiatives", "index.html#initiatives"),
            ("Contact", "contact.html"),
        ],
        "newsletter_h": "Newsletter",
        "newsletter_text_html": 'Abonnez-vous pour recevoir nos dernières publications, '
                                'une fois par mois. En vous abonnant, vous acceptez notre '
                                '<a href="politique-confidentialite.html" style="text-decoration:underline">politique de confidentialité</a>.',
        "newsletter_label": "Adresse e-mail",
        "newsletter_placeholder": "Saisissez votre adresse e-mail",
        "newsletter_button": "S'abonner",
        "legal_links": [
            ("Mentions légales", "mentions-legales.html"),
            ("Politique de confidentialité", "politique-confidentialite.html"),
            ("Accessibilité", "accessibilite.html"),
            ("Plan du site", "sitemap.html"),
        ],
        "by": "Par",
        "read_suffix": "min de lecture",
        "news": {
            "title": "Actualités & Analyses · Africa Governance Institute",
            "description": "Actualités, rapports et analyses de l'Institut Africain de la "
                           "Gouvernance sur les enjeux de gouvernance et d'économie du continent.",
            "author_meta": "Institut Africain de la Gouvernance",
            "og_title": "Actualités & Analyses · Africa Governance Institute",
            "og_description": "Rapports et analyses de l'Institut Africain de la Gouvernance.",
            "og_image_alt": "Actualités & Analyses",
            "crumb_home": "Accueil",
            "crumb_now": "Actualités",
            "eyebrow": "Salle de presse",
            "h1": "Actualités & Analyses",
            "deck": "Rapports et analyses de l'Institut Africain de la Gouvernance sur les "
                    "enjeux de gouvernance et d'économie qui façonnent le continent.",
            "more_h2": "De nouvelles analyses paraissent ici tout au long de l'année.",
            "more_p": "Les rapports sont publiés au fil de nos recherches et de nos "
                      "événements, les plus récents en premier. Abonnez-vous pour être "
                      "averti de la prochaine parution.",
            "more_link": "S'abonner aux actualités",
        },
    },
}
