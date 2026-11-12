from typing import List

from sqlmodel import Session, select
from sqlalchemy.engine import Engine
from models.municipalities import Municipality  # Your SQLModel table definition
import csv

MUNICIPALITIES_DATA_FILE = "resources/data/seed_municipality.csv"


def seed_data_from_csv(csv_file_path: str) -> List[Municipality]:
    items_to_add: List[Municipality] = []
    with open(csv_file_path, mode="r", encoding="utf-8") as file:
        # csv.DictReader automatically maps rows to dictionaries using the header row
        reader = csv.DictReader(file)

        for row in reader:
            # Instantiate the SQLModel object (data types are validated automatically)
            item = Municipality(
                municipality_code=row["municipality_code"],
                municipality_name=row["municipality_name"],
                continent=row["continent"],
                water_body=row["water_body"],
                country=row["country"],
                country_code=row["country_code"],
                state_province=row["state_province"],
                county=row["county"],
                inspireid=row["inspireid"],
                natlevel=row["natlevel"],
                netcode=row["netcode"],
                codnut1=row["codnut1"],
                codnut2=row["codnut2"],
                codnut3=row["codnut3"]
            )
            items_to_add.append(item)
    return items_to_add


def seed_municipalities_data(engine: Engine):
    with Session(engine) as session:
        # Check if data already exists to avoid duplication
        existing_count = session.exec(select(Municipality)).first()
        if existing_count:
            return  # Already seeded

        municipalities = seed_data_from_csv(MUNICIPALITIES_DATA_FILE)

        session.add_all(municipalities)
        session.commit()
