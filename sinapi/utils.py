from contextlib import suppress

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
    estados_response: EstadoResponse = await service.estados(
        term=None,
        order="name",
        direction="asc",
        search_type="contains",
        page=None,
        limit=None,
    )

    def filtrar_estados(e: EstadoResponseItem):
        return e.uf in ['SC','SP','SE','TO']

    result = list(filter(filtrar_estados, set(estados_response.items)))

    return sorted(list(result), key=lambda item: item.id)


if __name__ == "__main__":
    import asyncio

    async def main():
        async with SinapiService(login, senha) as service:
            await get_estados_a_cadastrar(service)

    asyncio.run(main())
