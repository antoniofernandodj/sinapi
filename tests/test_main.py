import sys
import pathlib

sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))

from sinapi.api.schema import InsumoComposicaoTabelaResponse
from sinapi.database import DATABASE_INSUMOS_URL2, get_session_local
from sinapi.models import InsumoComposicaoTabela


SessionLocal = get_session_local(DATABASE_INSUMOS_URL2, echo=False)

ids = [13364568, 13364569, 13364571, 13364573, 13364574]


def test_buscar_composicao():

    for id in ids:
        with SessionLocal() as session:

            composicao = session.query(InsumoComposicaoTabela).filter_by(id=id).first()

            assert composicao

            assert isinstance(composicao.to_pydantic(), InsumoComposicaoTabelaResponse)
