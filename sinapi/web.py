from pickle import NONE
from typing import Any, AsyncGenerator

from sinapi.api.schema import Mes

try:
    from sinapi.api.schema import EstadoResponseItem, InsumosResponse
    from sinapi.api import SinapiService
    from sinapi.utils import get_estados_a_cadastrar
except:
    from api import SinapiService
    from api.schema import EstadoResponseItem, InsumosResponse
    from utils import get_estados_a_cadastrar

login = "lsouza17@gmail.com"
senha = "eflEs2cF"

meses = [
    Mes(value=i, text=str(i)) for i in range(1, 13)
]

ESTADOS_RESPONSE = None


async def get_insumos_or_compositions(
    ano: str,
    composicao=True
) -> AsyncGenerator[tuple[InsumosResponse, EstadoResponseItem], Any]:
    async with SinapiService(login, senha) as service:
        ESTADOS_RESPONSE = await get_estados_a_cadastrar(service)

    async with SinapiService(login, senha) as service:
        try:
            for estado_response in ESTADOS_RESPONSE:
                uf = estado_response.uf
                for mes in meses:
                    if mes.value in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
                        continue
                    
                    print(f'Buscando para {ano}, {mes.value}, {uf}, {composicao}')
                    async for insumo_response in service.insumos_todos(
                        ano=ano, mes=mes.value, uf=uf, composicao=composicao,
                    ):
                        print(f'I: {insumo_response.totalRows}')
                        yield (insumo_response, estado_response)


        except Exception as error:
            import traceback

            traceback.print_exc()
            print(error)
            print(type(error))
            # logger.error(f"An error occurred: {error}")
