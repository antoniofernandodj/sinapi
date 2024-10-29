from contextlib import suppress
from typing import Optional

from sinapi.api.schema import EstadoResponseItem


try:
    from sinapi.api.schema import EstadoResponse
    from sinapi.api import SinapiService
    from sinapi.database import Session
    from sinapi.models import Estado
except:
    from api import SinapiService
    from database import Session
    from api.schema import EstadoResponse
    from models import Estado

login = "lsouza17@gmail.com"
senha = "eflEs2cF"


async def get_estados_a_cadastrar(service: SinapiService) -> list[EstadoResponseItem]:
    estados_response: Optional[EstadoResponse] = await service.estados(
        term=None,
        order="name",
        direction="asc",
        search_type="contains",
        page=None,
        limit=None,
    )

    def filtrar_estados(estado: EstadoResponseItem):
        return estado.uf in ['TO']

    estados_response_items = estados_response.items if estados_response else []
    result = list(filter(filtrar_estados, set(estados_response_items)))

    return sorted(list(result), key=lambda item: item.id)


if __name__ == "__main__":
    import asyncio

    async def main():
        async with SinapiService(login, senha) as service:
            await get_estados_a_cadastrar(service)

    asyncio.run(main())
