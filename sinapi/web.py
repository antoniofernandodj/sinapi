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

meses = [Mes(value=i, text=str(i)) for i in range(1, 13)]


async def get_insumos_or_compositions(
    ano: str, composicao=None
) -> AsyncGenerator[InsumosResponse, Any]:
    service = SinapiService(login, senha)
    estados_response = await get_estados_a_cadastrar(service)

    try:
        for estado_response in estados_response:
            uf = estado_response.uf
            for mes in meses:

                print(f"Buscando para {ano}, {mes.value}, {uf}, {composicao}")
                async for insumo_response in service.insumos_todos(
                    ano=ano,
                    mes=mes.value,
                    uf=uf,
                    composicao=composicao,
                ):

                    yield insumo_response

    except Exception as error:
        import traceback

        traceback.print_exc()
        print(error)
        print(type(error))
        # logger.error(f"An error occurred: {error}")
