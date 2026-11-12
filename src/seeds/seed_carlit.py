from sqlmodel import Session, select
from sqlalchemy.engine import Engine
from models.carlit import Carlit  # Your SQLModel table definition


def seed_carlit_data(engine: Engine):
    with Session(engine) as session:
        # Check if data already exists to avoid duplication
        existing_count = session.exec(select(Carlit)).first()
        if existing_count:
            return  # Already seeded

        carlit_data = [
            Carlit(carlit_name="Algas verdes", remarks="Cinturón superficial sublitoral de Ulva y Cladophora",
                   sensitivity_level=3),
            Carlit(carlit_name="Arrecife de Posidonia", remarks="Arrecife barrera de P. oceanica",
                   sensitivity_level=20),
            Carlit(carlit_name="Corallina", remarks="Cinturón de Corallina elongata sin Cystoseira",
                   sensitivity_level=8),
            Carlit(carlit_name="Corallinas incrustantes",
                   remarks="Cinturón superficial sublitoral de Lithophyllum incrustans, Neogoniolithon "
                           "brassica-florida y otras coralináceas incrustantes",
                   sensitivity_level=6),
            Carlit(carlit_name="Cymodocea nodosa", remarks="Praderas de Cymodocea nodosa", sensitivity_level=20),
            Carlit(carlit_name="Cystoseira balearica", remarks="Poblamientos de C. balearica", sensitivity_level=20),
            Carlit(carlit_name="Cystoseira compressa", remarks="Poblaciones de C. compressa v. compressa",
                   sensitivity_level=12),
            Carlit(carlit_name="Cystoseira crinita", remarks="Poblamientos de C. crinita", sensitivity_level=20),
            Carlit(carlit_name="Cystoseira mediterranea 1",
                   remarks="Manchas raras y dispersas de C. mediterranea / stricta", sensitivity_level=10),
            Carlit(carlit_name="Cystoseira mediterranea 2", remarks="Manchas dispersas de C. mediterranea / stricta",
                   sensitivity_level=12),
            Carlit(carlit_name="Cystoseira mediterranea 3",
                   remarks="Abundantes manchas densas de C. mediterranea / stricta", sensitivity_level=15),
            Carlit(carlit_name="Cystoseira mediterranea 4",
                   remarks="Cinturón casi continuo de C. mediterranea / stricta", sensitivity_level=19),
            Carlit(carlit_name="Cystoseira mediterranea 5", remarks="Cinturón continuo de C. mediterranea / stricta",
                   sensitivity_level=20),
            Carlit(carlit_name="Cystoseira protegida",
                   remarks="Poblaciones de C. foeniculata/barbata/spinosa v. tenuior /compressa v. pustulata",
                   sensitivity_level=20),
            Carlit(carlit_name="Haliptilon", remarks="Cinturón de Haliptilon virgatum sin Cystoseira",
                   sensitivity_level=8),
            Carlit(carlit_name="Mytilus", remarks="Lechos de mejillones (Mytilus galloprovincialis) sin Cystoseira",
                   sensitivity_level=6),
            Carlit(carlit_name="Trottoir", remarks="Cornisas de Lithophyllum byssoides", sensitivity_level=20),
            Carlit(carlit_name="Verde azuladas",
                   remarks="Comunidades Dominadas Por Cianobacterias y Derbesia tenuissima", sensitivity_level=1),
            Carlit(carlit_name="Zostera noltii", remarks="Praderas de Zostera noltii", sensitivity_level=20)
        ]
        session.add_all(carlit_data)
        session.commit()
