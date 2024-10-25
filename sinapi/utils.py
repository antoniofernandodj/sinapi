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


async def get_estados_a_cadastrar(service: SinapiService):
    estados_response: EstadoResponse = await service.estados(
        term=None,
        order="name",
        direction="asc",
        search_type="contains",
        page=None,
        limit=None
    )
    estados_disponiveis = set(estados_response.items)
    with Session() as session:
        estados_cadastrados_sqla = session.query(Estado).all()
    estados_cadastrados_list = [e.to_pydantic() for e in estados_cadastrados_sqla]
    ultimo_estado = estados_cadastrados_list[-1]
    estados_cadastrados = set(estados_cadastrados_list)
    estados_a_cadastrar = estados_disponiveis.difference(estados_cadastrados)
    estados_a_cadastrar.add(ultimo_estado)
    return sorted(list(estados_a_cadastrar), key=lambda item: item.id)



if __name__ == "__main__":
    import asyncio

    async def main():
        async with SinapiService(login, senha) as service:
            await get_estados_a_cadastrar(service)


    asyncio.run(main())