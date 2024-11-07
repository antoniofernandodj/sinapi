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

login = "lsouza17@gmail.com"
senha = "eflEs2cF"

# login = "teste@teste.com.br"
# senha = "teste"


ufs = {
    # "AC",
    # "AL",
    # "AP",
    # "AM",
    # "BA": [1],
    "CE": list(range(1, 9)),
    "DF": list(range(1, 9)),
    "ES": list(range(1, 9)),
    "GO": list(range(1, 9)),
    "MA": list(range(1, 9)),
    # "MT": list(range(1, 9)),
    # "MS": list(range(1, 9)),
    # "MG": list(range(1, 9)),
    # "PA": list(range(1, 9)),
    # "PB": list(range(1, 9)),
    "PR": list(range(1, 5)),
    # "PE": list(range(1, 9)),
    # "PI": list(range(1, 9)),
    "RJ": list(range(1, 9)),
    "RN": list(range(1, 9)),
    # "RS": list(range(1, 9)),
    "RO": list(range(1, 9)),
    "RR": list(range(1, 9)),
    # "SC": list(range(1, 9)),
    # "SP": list(range(1, 9)),
    # "SE": list(range(1, 9)),
    "TO": list(range(1, 9)),
}


async def get_insumos_or_compositions(composicao=None):

    ano = str(datetime.date.today().year)
    service = SinapiService(login, senha)

    try:
        for composicao in [False, True]:
            for uf, meses in ufs.items():
                for mes in meses:
                    print(
                        f"Buscando para ano: {ano}, mes: {mes}, uf: {uf}, {composicao}"
                    )
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
