"""Synchronisation NON DESTRUCTIVE du schéma de la base avec les modèles.

Crée les tables manquantes et ajoute les colonnes manquantes aux tables
existantes, sans jamais supprimer ni modifier de données. Utile pour mettre à
jour une base de production déjà remplie, sans terminal (via la page /setup).
"""
from sqlalchemy import inspect, text

from models import db


def sync_schema():
    """Renvoie (tables_créées, colonnes_ajoutées). Ne supprime jamais rien."""
    engine = db.engine
    before = set(inspect(engine).get_table_names())

    # 1) Tables manquantes.
    db.metadata.create_all(bind=engine)
    created = [t.name for t in db.metadata.sorted_tables if t.name not in before]

    # 2) Colonnes manquantes sur les tables déjà existantes.
    insp = inspect(engine)
    dialect = engine.dialect
    added = []
    for table in db.metadata.sorted_tables:
        if table.name in created or table.name not in before:
            continue
        have = {c["name"] for c in insp.get_columns(table.name)}
        for col in table.columns:
            if col.name in have:
                continue
            col_type = col.type.compile(dialect=dialect)
            # Ajout en NULL : sûr sur une table déjà remplie ; l'app fournit les
            # valeurs aux insertions suivantes.
            db.session.execute(text(
                f'ALTER TABLE `{table.name}` ADD COLUMN `{col.name}` {col_type} NULL'
            ))
            added.append(f"{table.name}.{col.name}")
    if added:
        db.session.commit()
    return created, added
