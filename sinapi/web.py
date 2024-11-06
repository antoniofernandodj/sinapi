import datetime
from pickle import NONE
from typing import Any, AsyncGenerator

from sinapi.api.schema import Mes

try:
    from sinapi.api.schema import EstadoResponseItem, InsumosResponse
    from sinapi.api import SinapiService
    from sinapi.utils import get_estados_a_cadastrar
except:
    from api import SinapiService  # type: ignore
    from api.schema import EstadoResponseItem, InsumosResponse
    from utils import get_estados_a_cadastrar

# login = "lsouza17@gmail.com"
# senha = "eflEs2cF"

login = "teste@teste.com.br"
senha = "teste"


ufs = {
    # "AC",
    # "AL",
    # "AP",
    # "AM",
    "BA": [1],
    "CE": list(range(1, 13)),
    "DF": list(range(1, 13)),
    "ES": list(range(1, 13)),
    "GO": list(range(1, 13)),
    "MA": list(range(1, 13)),
    "MT": list(range(1, 13)),
    "MS": list(range(1, 13)),
    "MG": list(range(1, 13)),
    "PA": list(range(1, 13)),
    "PB": list(range(1, 13)),
    "PR": list(range(1, 13)),
    "PE": list(range(1, 13)),
    "PI": list(range(1, 13)),
    "RJ": list(range(1, 13)),
    "RN": list(range(1, 13)),
    "RS": list(range(1, 13)),
    "RO": list(range(1, 13)),
    "RR": list(range(1, 13)),
    "SC": list(range(1, 13)),
    "SP": list(range(1, 13)),
    "SE": list(range(1, 13)),
    "TO": list(range(1, 13)),
}


async def get_insumos_or_compositions(composicao=True):

    ano = str(datetime.date.today().year)
    service = SinapiService(login, senha)

    try:
        for uf, meses in ufs.items():
            for mes in meses:
                print(f"Buscando para ano: {ano}, mes: {mes}, uf: {uf}, {composicao}")
                async for item in service.insumos_todos2(
                    ano=ano,
                    mes=mes,
                    uf=uf,
                    composicao=composicao,
                ):
                    # print(item)
                    yield item

    except Exception as error:
        import traceback

        traceback.print_exc()
        print(error)
        print(type(error))
        # logger.error(f"An error occurred: {error}")
