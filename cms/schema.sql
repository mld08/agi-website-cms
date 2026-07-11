-- Schema MySQL de reference (genere depuis models.py).
-- 'flask --app app init-db' cree ces tables automatiquement via SQLAlchemy.
-- Encodage utf8mb4 pour accents et caracteres speciaux.

SET NAMES utf8mb4;


CREATE TABLE IF NOT EXISTS applications (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	created_at DATETIME, 
	status VARCHAR(20) NOT NULL, 
	lang VARCHAR(2), 
	nom VARCHAR(160), 
	prenom VARCHAR(160), 
	email VARCHAR(190), 
	telephone VARCHAR(60), 
	date_naissance VARCHAR(40), 
	genre VARCHAR(40), 
	nationalite VARCHAR(120), 
	pays_residence VARCHAR(120), 
	ville VARCHAR(120), 
	tranche_age VARCHAR(40), 
	profession VARCHAR(200), 
	organisation VARCHAR(200), 
	langues VARCHAR(200), 
	statut VARCHAR(400), 
	domaines VARCHAR(400), 
	motivation TEXT, 
	experience TEXT, 
	contribution TEXT, 
	data_json TEXT, 
	cv_file VARCHAR(300), 
	lettre_file VARCHAR(300), 
	identite_file VARCHAR(300), 
	projet_file VARCHAR(300), 
	PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS articles (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	slug VARCHAR(160) NOT NULL, 
	status VARCHAR(16) NOT NULL, 
	pub_date DATE NOT NULL, 
	managed_detail BOOL NOT NULL, 
	author VARCHAR(120) NOT NULL, 
	read_minutes INTEGER NOT NULL, 
	image VARCHAR(200) NOT NULL, 
	image_w INTEGER NOT NULL, 
	image_h INTEGER NOT NULL, 
	image_alt_en VARCHAR(300), 
	image_alt_fr VARCHAR(300), 
	category_en VARCHAR(120), 
	category_fr VARCHAR(120), 
	title_en VARCHAR(300) NOT NULL, 
	title_fr VARCHAR(300) NOT NULL, 
	body_en TEXT, 
	body_fr TEXT, 
	meta_description_en VARCHAR(300), 
	meta_description_fr VARCHAR(300), 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	UNIQUE (slug)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS programs (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	slug VARCHAR(160) NOT NULL, 
	status VARCHAR(16) NOT NULL, 
	sort_index INTEGER NOT NULL, 
	anchor VARCHAR(60), 
	category_en VARCHAR(160), 
	category_fr VARCHAR(160), 
	title_en VARCHAR(300), 
	title_fr VARCHAR(300), 
	where_en VARCHAR(300), 
	where_fr VARCHAR(300), 
	lead_en TEXT, 
	lead_fr TEXT, 
	points_en TEXT, 
	points_fr TEXT, 
	fund_en VARCHAR(400), 
	fund_fr VARCHAR(400), 
	image VARCHAR(200), 
	image_w INTEGER, 
	image_h INTEGER, 
	image_alt_en VARCHAR(300), 
	image_alt_fr VARCHAR(300), 
	link_href VARCHAR(300), 
	link_label_en VARCHAR(120), 
	link_label_fr VARCHAR(120), 
	link_external BOOL, 
	PRIMARY KEY (id), 
	UNIQUE (slug)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS publish_log (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	created_at DATETIME, 
	user_email VARCHAR(190), 
	pages_count INTEGER, 
	status VARCHAR(16), 
	detail VARCHAR(400), 
	PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS resources (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	status VARCHAR(16) NOT NULL, 
	sort_index INTEGER NOT NULL, 
	kind VARCHAR(40), 
	title_en VARCHAR(300), 
	title_fr VARCHAR(300), 
	subtitle_en VARCHAR(300), 
	subtitle_fr VARCHAR(300), 
	pdf_file VARCHAR(200), 
	video_embed VARCHAR(400), 
	video_image VARCHAR(200), 
	video_image_w INTEGER, 
	video_image_h INTEGER, 
	image VARCHAR(200), 
	image_w INTEGER, 
	image_h INTEGER, 
	variant VARCHAR(16), 
	PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS team_members (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	slug VARCHAR(160) NOT NULL, 
	status VARCHAR(16) NOT NULL, 
	sort_index INTEGER NOT NULL, 
	name_en VARCHAR(160) NOT NULL, 
	name_fr VARCHAR(160) NOT NULL, 
	role_en VARCHAR(200), 
	role_fr VARCHAR(200), 
	bio_en TEXT, 
	bio_fr TEXT, 
	photo VARCHAR(200), 
	photo_w INTEGER, 
	photo_h INTEGER, 
	photo_hover VARCHAR(200), 
	photo_hover_w INTEGER, 
	photo_hover_h INTEGER, 
	accent_color VARCHAR(16), 
	has_page BOOL, 
	PRIMARY KEY (id), 
	UNIQUE (slug)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS users (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	email VARCHAR(190) NOT NULL, 
	password_hash VARCHAR(255) NOT NULL, 
	`role` VARCHAR(20) NOT NULL, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	UNIQUE (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
