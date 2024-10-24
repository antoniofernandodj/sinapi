from typing import Any, AsyncGenerator

try:
    from sinapi.api.schema import EstadoResponse, EstadoResponseItem, InsumosResponse
    from sinapi.api import SinapiService
    from sinapi.utils import get_estados_a_cadastrar
except:
    from api import SinapiService
    from api.schema import EstadoResponse, EstadoResponseItem, InsumosResponse
    from utils import get_estados_a_cadastrar


# logger = logging.getLogger(Path(__file__).name)
# handler = logging.FileHandler(filename="sinapi.log", mode="w")
# logger.addHandler(handler)


login = "lsouza17@gmail.com"
senha = "eflEs2cF"


async def get_insumos_or_compositions(
    ano: str,
    composicao=True
) -> AsyncGenerator[tuple[InsumosResponse, EstadoResponseItem], Any]:

    async with SinapiService(login, senha) as service:
        try:
            estados_response = await get_estados_a_cadastrar(service)

            for estado_response in estados_response:
                uf = estado_response.uf
                meses = await service.meses_importados(
                    tipo_tabela="SINAPI", uf=uf, ano=ano
                )
                for mes in meses:
                    async for insumo_response in service.insumos_todos(
                        ano=ano,
                        mes=mes.value,
                        uf=uf,
                        composicao=composicao,
                    ):
                        yield (insumo_response, estado_response)


        except Exception as error:
            import traceback

            traceback.print_exc()
            print(error)
            print(type(error))
            # logger.error(f"An error occurred: {error}")
