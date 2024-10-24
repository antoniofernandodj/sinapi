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


async def get_estados_a_cadastrar():
    async with SinapiService(login, senha) as service:

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

        estados_cadastrados_list = [
            estado.to_pydantic() for estado in estados_cadastrados_sqla
        ]

        ultimo_estado = estados_cadastrados_list[-1]
        estados_cadastrados = set(estados_cadastrados_list)
        estados_a_cadastrar = list(estados_disponiveis.difference(estados_cadastrados))
        estados_a_cadastrar.append(ultimo_estado)

        return estados_a_cadastrar
