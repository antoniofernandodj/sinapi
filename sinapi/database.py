from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

try:
    from models import Base
except:
    from sinapi.models import Base


SGBD_URL = "mysql+pymysql://itemize:I*2021t1201@localhost"
DATABASE_INSUMOS_URL = "mysql+pymysql://itemize:I*2021t1201@localhost/sinapi"

with create_engine(SGBD_URL, echo=False).connect() as connection:
    connection.execute(text("CREATE DATABASE IF NOT EXISTS sinapi"))

engine = create_engine(DATABASE_INSUMOS_URL, echo=False)
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)


def get_session():
    from sqlalchemy.orm import sessionmaker

    DATABASE_INSUMOS_URL = "mysql+pymysql://itemize:I*2021t1201@localhost/sinapi"

    engine = create_engine(DATABASE_INSUMOS_URL, echo=False)
    Session = sessionmaker(bind=engine)
    return Session
