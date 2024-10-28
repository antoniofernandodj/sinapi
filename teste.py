import asyncio
from typing import Any, AsyncGenerator

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


async def get_insumos_or_compositions():

    async with SinapiService(login, senha) as service:

        estados_response = await get_estados_a_cadastrar(service)

        print(estados_response)


asyncio.run(get_insumos_or_compositions())