from datetime import datetime
import logging
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List
from api import SinapiService
import aiofiles
import json

from sinapi.api.schema import EstadoResponse, EstadoResponseItem, InsumosResponse


logger = logging.getLogger(Path(__file__).name)
handler = logging.FileHandler(filename="sinapi.log", mode="w")
logger.addHandler(handler)


login = "lsouza17@gmail.com"
senha = "eflEs2cF"


async def get_estados() -> AsyncGenerator[EstadoResponse, Any]:
    async with SinapiService(login, senha) as service:
        yield await service.estados(
            term=None,
            order="name",
            direction="asc",
            search_type="contains",
            page=None,
            limit=None
        )


async def get_insumos_or_compositions(
    ano: str,
    composicao=True
) -> AsyncGenerator[tuple[InsumosResponse, EstadoResponseItem], Any]:

    async with SinapiService(login, senha) as service:
        try:
            estados_response = await service.estados(
                term=None,
                order="name",
                direction="asc",
                search_type="contains",
                page=None,  # page=1,
                limit=None  # limit=20
            )

            for estado_response in estados_response.items:
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
            logger.error(f"An error occurred: {error}")
