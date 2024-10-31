from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

try:
    from models import Base
except:
    from sinapi.models import Base


SGBD_URL = "mysql+pymysql://itemize:I*2021t1201@localhost"
DATABASE_INSUMOS_URL = "mysql+pymysql://itemize:I*2021t1201@localhost/sinapi"
DATABASE_INSUMOS_URL2 = "mysql+pymysql://admin:I*2021t1201@mng.itemize.com.br/sinapi"


# with create_engine(SGBD_URL, echo=False).connect() as connection:
#     connection.execute(text("CREATE DATABASE IF NOT EXISTS sinapi"))

engine = create_engine(DATABASE_INSUMOS_URL, echo=False)
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)


def get_session_local(url, echo):
    engine = create_engine(url, echo=echo)
    return sessionmaker(bind=engine)
