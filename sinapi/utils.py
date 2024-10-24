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
    print('estados_disponiveis')
    print([estado.uf for estado in estados_disponiveis])

    with Session() as session:
        estados_cadastrados_sqla = session.query(Estado).all()

    estados_cadastrados_list = [
        estado.to_pydantic() for estado in estados_cadastrados_sqla
    ]

    ultimo_estado = estados_cadastrados_list[-1]
    print('ultimo_estado')
    print(ultimo_estado.uf)

    estados_cadastrados = set(estados_cadastrados_list)
    print('estados_cadastrados')
    print([estado.uf for estado in estados_cadastrados])

    estados_a_cadastrar = list(estados_disponiveis.difference(estados_cadastrados))
    estados_a_cadastrar.append(ultimo_estado)
    print('estados_a_cadastrar')
    print([estado.uf for estado in estados_a_cadastrar])

    return estados_a_cadastrar