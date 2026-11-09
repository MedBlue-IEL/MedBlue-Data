from sqlmodel import Session, select
from sqlalchemy.engine import Engine
from models.habitats import Habitat  # Your SQLModel table definition


def seed_habitats_data(engine: Engine):
    with Session(engine) as session:
        # Check if data already exists to avoid duplication
        existing_count = session.exec(select(Habitat)).first()
        if existing_count:
            return  # Already seeded

        habitats = [
            Habitat(habitat_code="1110", habitat_name="Bancos de arena cubiertos permanentemente por agua marina, "
                                                          "poco profunda"),
            Habitat(habitat_code="1120", habitat_name="Praderas de Posidonia(Posidonion oceanicae)"),
            Habitat(habitat_code="1170", habitat_name="Arrecifes"),
            Habitat(habitat_code="1180", habitat_name="Estructuras submarinas causadas por emisiones de gases"),
            Habitat(habitat_code="8330", habitat_name="Cuevas marinas sumergidas o semisumergidas"),
        ]
        session.add_all(habitats)
        session.commit()
