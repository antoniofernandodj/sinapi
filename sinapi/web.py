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


ufs_meses = {
    # "AC",
    # "AL",
    # "AP",
    # "AM",
    # "BA": [1],
    # "CE": range(1, 9),
    # "DF": range(1, 9),
    # "ES": range(1, 9),
    # "GO": range(1, 9),
    # "MA": range(1, 9),
    # "MT": range(1, 9),
    # "MS": range(1, 9),
    # "MG": range(1, 9),
    # "PA": range(1, 9),
    # "PB": range(1, 9),
    # "PR": range(1, 5),
    # "PE": range(1, 9),
    # "PI": range(1, 9),
    # "RJ": range(1, 9),
    # "RN": range(1, 9),
    "RS": range(5, 6),
    # "RO": range(1, 9),
    # "RR": range(1, 9),
    # "SC": range(1, 9),
    # "SP": range(1, 9),
    # "SE": range(1, 9),
    # "TO": range(1, 9),
}


async def get_insumos_or_compositions(composicao=False):

    ano = str(datetime.date.today().year)
    service = SinapiService(login, senha)

    try:
        for uf, meses in ufs_meses.items():
            for mes in meses:
                print(
                    f"Buscando para ano: {ano}, mes: {mes}, uf: {uf}, composicao: {composicao}"
                )
                async for item in service.insumos_todos2(
                    ano=ano,
                    mes=mes,
                    uf=uf,
                    composicao=composicao,
                ):
                    print(item.id)
                    yield item

    except Exception as error:
        import traceback

        traceback.print_exc()
        print(error)
        print(type(error))
        # logger.error(f"An error occurred: {error}")
