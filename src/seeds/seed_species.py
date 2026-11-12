from typing import List

from sqlmodel import Session, select
from sqlalchemy.engine import Engine
from models.species import Species  # Your SQLModel table definition
import csv

SPECIES_DATA_FILE = "resources/data/seed_species.csv"


def seed_data_from_csv(csv_file_path: str) -> List[Species]:
    items_to_add: List[Species] = []
    with open(csv_file_path, mode="r", encoding="utf-8") as file:
        # csv.DictReader automatically maps rows to dictionaries using the header row
        reader = csv.DictReader(file)

        for row in reader:
            # Instantiate the SQLModel object (data types are validated automatically)
            item = Species(
                scientific_name=row["scientific_name"],
                scientific_name_id=row["scientific_name_id"],
                taxon_id=row["taxon_id"],
                scientific_name_authorship=row["scientific_name_authorship"],
                kingdom=row["kingdom"],
                phylum=row["phylum"],
                species_class = row["species_class"],
                order = row["order"],
                family = row["family"],
                genus = row["genus"],
                specific_epithet = row["specific_epithet"],
                infraspecific_epithet = row["infraspecific_epithet"],
                taxon_rank = row["taxon_rank"],
                taxon_remarks = row["taxon_remarks"]
            )
            items_to_add.append(item)
    return items_to_add


def seed_species_data(engine: Engine):
    with Session(engine) as session:
        # Check if data already exists to avoid duplication
        existing_count = session.exec(select(Species)).first()
        if existing_count:
            return  # Already seeded

        species = seed_data_from_csv(SPECIES_DATA_FILE)

        session.add_all(species)
        session.commit()
