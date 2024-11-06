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


meses = [mes for mes in range(1, 13)]

ufs = [
    # "AC",
    # "AL",
    # "AP",
    # "AM",
    # "BA",
    "CE",
    "DF",
    "ES",
    "GO",
    "MA",
    "MT",
    "MS",
    "MG",
    "PA",
    "PB",
    "PR",
    "PE",
    "PI",
    "RJ",
    "RN",
    "RS",
    "RO",
    "RR",
    "SC",
    "SP",
    "SE",
    "TO",
]


async def get_insumos_or_compositions(composicao=True):

    ano = str(datetime.date.today().year)
    service = SinapiService(login, senha)

    try:
        for mes in meses:
            for uf in ufs:
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
