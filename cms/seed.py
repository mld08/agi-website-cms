"""Données de départ : les 3 articles déjà présents sur le site, pour que la
page Actualités générée corresponde exactement à l'existant.
"""
from datetime import date
from models import db, Article, TeamMember, Program, Resource

ARTICLES = [
    dict(
        slug="coastal-futures",
        status="published",
        managed_detail=False,  # page sur-mesure conservée (template/en|fr/coastal-futures.html)
        pub_date=date(2025, 6, 10),
        author="Africa Governance Institute",
        read_minutes=12,
        image="coastal/cf-room.webp",
        image_w=1080, image_h=720,
        image_alt_en="The Coastal Futures launch ceremony at the Terrou-Bi Hotel, Dakar",
        image_alt_fr="Cérémonie de lancement de Coastal Futures à l'Hôtel Terrou-Bi, Dakar",
        category_en="Environmental Governance",
        category_fr="Gouvernance environnementale",
        title_en="Coastal Futures: the official launch in Dakar",
        title_fr="Coastal Futures : le lancement officiel à Dakar",
    ),
    dict(
        slug="us-tariffs",
        status="published",
        managed_detail=False,  # page sur-mesure conservée
        pub_date=date(2025, 5, 7),
        author="Maty Ndiaye",
        read_minutes=6,
        image="article-tariffs.webp",
        image_w=1551, image_h=1206,
        image_alt_en="What if the U.S. tariffs on 46 African countries are a wake-up call?",
        image_alt_fr="Et si les tarifs américains imposés à 46 pays africains étaient un signal d'alarme ?",
        category_en="Economics & Policy",
        category_fr="Économie & Politiques",
        title_en="What if the U.S. Tariffs on 46 African Countries are a Wake-up Call?",
        title_fr="Et si les tarifs américains imposés à 46 pays africains étaient un signal d'alarme ?",
    ),
    dict(
        slug="enhancing-africas-global-voice",
        status="published",
        managed_detail=False,  # page sur-mesure conservée
        pub_date=date(2023, 9, 20),
        author="Africa Governance Institute",
        read_minutes=7,
        image="global-voice/gv-signage.webp",
        image_w=1209, image_h=806,
        image_alt_en="Enhancing Africa's Global Voice, UN General Assembly 78 side event",
        image_alt_fr="Enhancing Africa's Global Voice, évènement parallèle de la 78e Assemblée générale des Nations Unies",
        category_en="Multilateralism & Diplomacy",
        category_fr="Multilatéralisme & Diplomatie",
        title_en="Enhancing Africa's Global Voice: a UNGA 78 side event in New York",
        title_fr="Enhancing Africa's Global Voice : un évènement parallèle de la 78e AGNU à New York",
    ),
]


def seed_articles() -> int:
    """Insère les articles manquants (idempotent par slug). Renvoie le nombre ajouté."""
    added = 0
    for data in ARTICLES:
        if not Article.query.filter_by(slug=data["slug"]).first():
            db.session.add(Article(**data))
            added += 1
    db.session.commit()
    return added


# Les 9 membres de l'équipe, dans l'ordre d'affichage (fidèle à about.html).
# has_page=True : carte cliquable (page sur-mesure existante). False : carte statique.
TEAM = [
    dict(slug="abdoulie-janneh", sort_index=1, has_page=True, accent_color="#B22F28",
         name_en="Dr. Abdoulie Janneh", name_fr="Dr Abdoulie Janneh",
         role_en="Director General & Chairman of the Board",
         role_fr="Directeur Général et Président du Conseil d'administration",
         photo="team/abdoulie-janneh.jpg", photo_w=900, photo_h=1200),
    dict(slug="maty-ndiaye", sort_index=2, has_page=True, accent_color="#5E6B27",
         name_en="Maty Ndiaye", name_fr="Maty Ndiaye",
         role_en="Director of Programs", role_fr="Directrice des Programmes",
         photo="team/maty-ndiaye.jpg", photo_w=900, photo_h=1350,
         photo_hover="team/maty-ndiaye-full.jpg", photo_hover_w=1067, photo_hover_h=1600),
    dict(slug="ndeye-coumba-diedhiou", sort_index=3, has_page=True, accent_color="#DD8728",
         name_en="Ndeye Coumba Diedhiou", name_fr="Ndeye Coumba Diedhiou",
         role_en="Chief, Operations & Resource Management",
         role_fr="Chargée des opérations et des ressources humaines",
         photo="team/ndeye-coumba-diedhiou.jpg", photo_w=900, photo_h=1350,
         photo_hover="team/ndeye-coumba-diedhiou-full.jpg", photo_hover_w=1067, photo_hover_h=1600),
    dict(slug="fanta-camara", sort_index=4, has_page=True, accent_color="#5E6B27",
         name_en="Fanta Camara", name_fr="Fanta Camara",
         role_en="Head, Climate & Youth Cluster",
         role_fr="Responsable du Cluster Climat & Jeunesse",
         photo="team/fanta-camara.jpg", photo_w=900, photo_h=1350,
         photo_hover="team/fanta-camara-full.jpg", photo_hover_w=1067, photo_hover_h=1600),
    dict(slug="coumba-sambe", sort_index=5, has_page=True, accent_color="#B22F28",
         name_en="Coumba Sambe", name_fr="Coumba Sambe",
         role_en="Program Analyst and International Relations Specialist",
         role_fr="Analyste de Programme et Spécialiste en Relations Internationales",
         photo="team/coumba-sambe.jpg", photo_w=900, photo_h=1350,
         photo_hover="team/coumba-sambe-full.jpg", photo_hover_w=1067, photo_hover_h=1600),
    dict(slug="saifi-dawalbet", sort_index=6, has_page=True, accent_color="#DD8728",
         name_en="Saïfi Dawalbet Hamit", name_fr="Saïfi Dawalbet Hamit",
         role_en="Legal Expert & Program Analyst",
         role_fr="Expert Juridique & Analyste de Programme",
         photo="team/saifi-dawalbet.jpg", photo_w=900, photo_h=1350,
         photo_hover="team/saifi-dawalbet-full.jpg", photo_hover_w=1067, photo_hover_h=1600),
    dict(slug="sirandou-sall", sort_index=7, has_page=False, accent_color="#E8B936",
         name_en="Sirandou Sall", name_fr="Sirandou Sall",
         role_en="Executive Assistant", role_fr="Assistante Administrative",
         photo="team/sirandou-sall.jpg", photo_w=900, photo_h=1350,
         photo_hover="team/sirandou-sall-full.jpg", photo_hover_w=1067, photo_hover_h=1600),
    dict(slug="ndjibou-cisse", sort_index=8, has_page=False, accent_color="#5E6B27",
         name_en="Ndjibou Cisse", name_fr="Ndjibou Cisse",
         role_en="Finance Officer", role_fr="Chargée des finances",
         photo="team/ndjibou-cisse.jpg", photo_w=860, photo_h=1292),
    dict(slug="abdou-lahat-thiam", sort_index=9, has_page=False, accent_color="#DD8728",
         name_en="Abdou Lahat Thiam", name_fr="Abdou Lahat Thiam",
         role_en="Driver", role_fr="Chauffeur",
         photo="team/abdou-lahat-thiam.jpg", photo_w=860, photo_h=1290,
         photo_hover="team/abdou-lahat-thiam-full.jpg", photo_hover_w=860, photo_hover_h=1290),
]


def seed_team() -> int:
    """Insère les membres manquants (idempotent par slug). Tous publiés."""
    added = 0
    for data in TEAM:
        if not TeamMember.query.filter_by(slug=data["slug"]).first():
            db.session.add(TeamMember(status="published", **data))
            added += 1
    db.session.commit()
    return added


# Les 5 programmes de la section « initiatives », fidèles à programs.html.
PROGRAMS = [
    dict(slug="coastal-futures", sort_index=1, anchor="coastal",
         category_en="Climate & Youth", category_fr="Climat & Jeunesse",
         title_en="Coastal Futures", title_fr="Coastal Futures",
         where_en="Five West African countries · Launched June 2026, Dakar",
         where_fr="Cinq pays d'Afrique de l'Ouest · Lancé en juin 2026, Dakar",
         lead_en="A regional initiative for coastal climate resilience and green entrepreneurship. Coastal Futures equips young people across West Africa to respond to coastal erosion, rising seas and the loss of ocean livelihoods, and to build businesses around them.",
         lead_fr="Une initiative régionale de résilience climatique côtière et d'entrepreneuriat vert. Coastal Futures outille les jeunes d'Afrique de l'Ouest pour répondre à l'érosion côtière, à la montée des eaux et à la perte des moyens de subsistance liés à l'océan, et pour en faire des activités.",
         points_en="Senegal, Guinea, Guinea-Bissau, Sierra Leone and Ghana.\n"
                   "A 2026–2027 roadmap connecting youth to international climate finance.\n"
                   "Built with the Ministry of Environment, AFD, Tree AID and regional partners.",
         points_fr="Sénégal, Guinée, Guinée-Bissau, Sierra Leone et Ghana.\n"
                   "Une feuille de route 2026–2027 reliant la jeunesse à la finance climatique internationale.\n"
                   "Construite avec le Ministère de l'Environnement, l'AFD, Tree AID et des partenaires régionaux.",
         fund_en="Convened by <strong>AGI</strong>", fund_fr="Organisée par <strong>l'IAG</strong>",
         image="coastal/cf-room.webp", image_w=1080, image_h=720,
         image_alt_en="The Coastal Futures launch ceremony in Dakar, June 2026",
         image_alt_fr="Cérémonie de lancement de Coastal Futures à Dakar, juin 2026",
         link_href="coastal-futures.html", link_label_en="Read the article",
         link_label_fr="Lire l'article", link_external=False),
    dict(slug="youth-empowerment-program", sort_index=2, anchor="yep",
         category_en="Youth & Entrepreneurship", category_fr="Jeunesse & Entrepreneuriat",
         title_en="Youth Empowerment Program", title_fr="Youth Empowerment Program",
         where_en="Sierra Leone · 2024–2025", where_fr="Sierra Leone · 2024–2025",
         lead_en="AGI is equipping 500 young Sierra Leoneans, with a focus on women, to build businesses and livelihoods, addressing youth unemployment and the gap in vocational training through training, mentorship and access to finance.",
         lead_fr="L'IAG outille 500 jeunes Sierra-Léonais, avec un accent sur les femmes, pour bâtir des entreprises et des moyens de subsistance, en répondant au chômage des jeunes et au déficit de formation professionnelle par la formation, le mentorat et l'accès au financement.",
         points_en="Entrepreneurial training, mentorship and networking.\n"
                   "Access to finance: microfinance, grants and funding pathways.\n"
                   "A local leadership pipeline, with young women at the centre.",
         points_fr="Formation entrepreneuriale, mentorat et mise en réseau.\n"
                   "Accès au financement : microfinance, subventions et pistes de financement.\n"
                   "Un vivier de leaders locaux, avec les jeunes femmes au centre.",
         fund_en="Funded by <strong>BADEA</strong> · Implemented by AGI",
         fund_fr="Financé par <strong>BADEA</strong> · Mis en œuvre par l'IAG",
         image="programs/yep-event.webp", image_w=1200, image_h=857,
         image_alt_en="A young participant speaking at a Youth Empowerment Program gathering",
         image_alt_fr="Une jeune participante prend la parole lors d'une rencontre du Youth Empowerment Program",
         link_href="https://africayep.com/", link_label_en="Visit the site",
         link_label_fr="Visiter le site", link_external=True),
    dict(slug="citizens-voice", sort_index=3, anchor="",
         category_en="Civil Society & Accountability", category_fr="Société Civile & Redevabilité",
         title_en="Enhancing Citizens' Voice and Accountability",
         title_fr="Renforcer la voix citoyenne et la redevabilité",
         where_en="Pan-African · Multi-year", where_fr="Panafricain · Pluriannuel",
         lead_en="The project strengthens non-state actors, civil society and grassroots organisations so that citizens can demand voice, transparency and accountability in the delivery of public services, turning research into practical tools they can use.",
         lead_fr="Le projet renforce les acteurs non étatiques, la société civile et les organisations de terrain afin que les citoyens puissent exiger voix, transparence et redevabilité dans la fourniture des services publics, en traduisant la recherche en outils concrets.",
         points_en="Public procurement and citizen monitoring of public contracts.\n"
                   "Domestic revenue mobilisation and fiscal citizenship.\n"
                   "Participation in budget formulation and oversight.",
         points_fr="Marchés publics et suivi citoyen des contrats publics.\n"
                   "Mobilisation des recettes intérieures et citoyenneté fiscale.\n"
                   "Participation à l'élaboration et au contrôle du budget.",
         image="jotaay.webp", image_w=1852, image_h=1256,
         image_alt_en="Delegates at an AGI civic accountability forum",
         image_alt_fr="Délégués lors d'un forum de l'IAG sur la redevabilité citoyenne"),
    dict(slug="democratic-accountability", sort_index=4, anchor="",
         category_en="Democracy & Rule of Law", category_fr="Démocratie & État de Droit",
         title_en="Promoting Democratic Accountability",
         title_fr="Promouvoir la redevabilité démocratique",
         where_en="Continental · Long-term", where_fr="Continental · Long terme",
         lead_en="This program supports the integrity of elections, the independence of oversight bodies and the responsiveness of state institutions, working alongside African states and civil society to put the principles of the African Charter into practice.",
         lead_fr="Ce programme soutient l'intégrité des élections, l'indépendance des organes de contrôle et la réactivité des institutions étatiques, aux côtés des États africains et de la société civile, pour traduire en pratique les principes de la Charte Africaine.",
         points_en="Electoral integrity and credible election management.\n"
                   "Stronger parliaments, audit and anti-corruption bodies.\n"
                   "Civic space: association, expression and assembly.",
         points_fr="Intégrité électorale et gestion crédible des scrutins.\n"
                   "Parlements, institutions de contrôle et organes anticorruption renforcés.\n"
                   "Espace civique : association, expression et réunion.",
         image="article-challenges.webp", image_w=1852, image_h=1256,
         image_alt_en="An AGI dialogue on democratic accountability in Africa",
         image_alt_fr="Un dialogue de l'IAG sur la redevabilité démocratique en Afrique"),
    dict(slug="governance-architecture", sort_index=5, anchor="",
         category_en="African Union & Frameworks", category_fr="Union Africaine & Cadres",
         title_en="African Governance Architecture",
         title_fr="Architecture Africaine de la Gouvernance",
         where_en="African Union · Addis Ababa & Dakar", where_fr="Union Africaine · Addis-Abeba & Dakar",
         lead_en="AGI supports the African Governance Architecture, the platform for dialogue between AU organs and Regional Economic Communities. We provide technical assistance, help draft charters and frameworks, and convene senior civil servants from across the continent.",
         lead_fr="L'IAG soutient l'Architecture Africaine de la Gouvernance, la plateforme de dialogue entre les organes de l'UA et les Communautés Économiques Régionales. Nous fournissons une assistance technique, contribuons à la rédaction de chartes et de cadres, et réunissons de hauts fonctionnaires de tout le continent.",
         points_en="Drafting support for AU charters and decentralisation frameworks.\n"
                   "60 senior civil servants trained across language regions.\n"
                   "350 expert profiles mapped in the AGI resource centre.",
         points_fr="Appui à la rédaction des chartes de l'UA et des cadres de décentralisation.\n"
                   "60 hauts fonctionnaires formés à travers les espaces linguistiques.\n"
                   "350 profils d'experts cartographiés dans le centre de ressources de l'IAG.",
         image="coastal/cf-table-partners.webp", image_w=1600, image_h=1066,
         image_alt_en="Senior officials at an AGI convening of African Union and regional partners",
         image_alt_fr="Hauts responsables lors d'une rencontre de l'IAG réunissant l'Union africaine et des partenaires régionaux"),
]


def seed_programs() -> int:
    added = 0
    for data in PROGRAMS:
        if not Program.query.filter_by(slug=data["slug"]).first():
            db.session.add(Program(status="published", **data))
            added += 1
    db.session.commit()
    return added


# Ressources : publications (PDF) et vidéos, fidèles à resources.html / ressources.html.
RESOURCES = [
    dict(kind="publication", sort_index=1,
         title_en="Coastal Futures, launch report", title_fr="Coastal Futures, rapport de lancement",
         subtitle_en="PDF · Report from the Dakar launch, June 2026",
         subtitle_fr="PDF · Rapport du lancement de Dakar, juin 2026",
         pdf_file="coastal-futures-rapport.pdf"),
    dict(kind="video", sort_index=1,
         title_en="Official launch video · Coastal Futures, Dakar",
         title_fr="Vidéo du lancement officiel · Coastal Futures, Dakar",
         video_embed="https://www.youtube-nocookie.com/embed/UkZbfYZiH90?autoplay=1",
         video_image="coastal/cf-room.webp", video_image_w=1080, video_image_h=720),
]

# Galerie photo (kind="gallery"). title_en/fr = texte alternatif ; variant = mise en page.
def _shot(idx, img, w, h, variant, alt_en, alt_fr):
    return dict(kind="gallery", sort_index=idx, variant=variant,
                image=f"coastal/{img}", image_w=w, image_h=h,
                title_en=alt_en, title_fr=alt_fr)

GALLERY = [
    _shot(1, "cf-audience.webp", 1600, 1066, "wide",
          "The audience at the Coastal Futures launch in Dakar",
          "Le public lors du lancement de Coastal Futures à Dakar"),
    _shot(2, "cf-interview.webp", 1080, 1920, "tall",
          "An interview on the sidelines of the Coastal Futures launch",
          "Une interview en marge du lancement de Coastal Futures"),
    _shot(3, "cf-panel1.webp", 1080, 720, "",
          "A panel discussion during Coastal Futures",
          "Une table ronde pendant Coastal Futures"),
    _shot(4, "cf-speaker-woman.webp", 1600, 1066, "",
          "A speaker addresses the Coastal Futures gathering",
          "Une intervenante s'adresse à l'assemblée de Coastal Futures"),
    _shot(5, "cf-greeting.webp", 1600, 1066, "",
          "Welcoming partners at the Coastal Futures convening",
          "Accueil des partenaires lors de la rencontre Coastal Futures"),
    _shot(6, "cf-table-partners.webp", 1600, 1066, "",
          "Partners seated at the Coastal Futures launch",
          "Des partenaires réunis au lancement de Coastal Futures"),
    _shot(7, "cf-panel2.webp", 1600, 1066, "wide",
          "A second panel at the Coastal Futures launch",
          "Une seconde table ronde au lancement de Coastal Futures"),
    _shot(8, "cf-table-women.webp", 1600, 1066, "",
          "Participants at the Coastal Futures launch",
          "Des participantes au lancement de Coastal Futures"),
    _shot(9, "cf-opening-seated.webp", 1080, 720, "",
          "The opening of the Coastal Futures ceremony",
          "L'ouverture de la cérémonie Coastal Futures"),
]
RESOURCES = RESOURCES + GALLERY


def seed_resources() -> int:
    added = 0
    for data in RESOURCES:
        exists = Resource.query.filter_by(kind=data["kind"], title_en=data["title_en"]).first()
        if not exists:
            db.session.add(Resource(status="published", **data))
            added += 1
    db.session.commit()
    return added
