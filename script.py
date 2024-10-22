import asyncio
from datetime import datetime
import logging
from pathlib import Path
from typing import Any, Dict, List
from sinapi.api import SinapiService
import aiofiles
import json

from sinapi.api.schema import InsumosResponseItem


logger = logging.getLogger(Path(__file__).name)
handler = logging.FileHandler(filename="sinapi.log", mode="w")
logger.addHandler(handler)


login = "lsouza17@gmail.com"
senha = "eflEs2cF"


def custom_converter(o):
    if isinstance(o, datetime):
        return o.isoformat()
    raise TypeError(f"Type {type(o)} not serializable")


class Completed(Exception): ...


async def download_insumos_or_compositions(
    filename: str,
    ano: str,
    composicao=True,
):
    async with (
        SinapiService(login, senha) as service,
        aiofiles.open(filename, "w") as f,
    ):
        try:
            estados_response = await service.estados(
                term=None,
                order="name",
                direction="asc",
                search_type="contains",
                page=None,
                limit=None
            )
            result: List[Dict[str, Any]] = []
            for estado_response in estados_response.items:
                uf = estado_response.uf
                meses_response = await service.meses_importados("SINAPI", uf, ano)
                meses = [mes_response.value for mes_response in meses_response]
                for mes in meses:
                    insumos: List[InsumosResponseItem]
                    insumos = await service.insumos_todos(
                        ano=ano, mes=mes, uf=uf,composicao=composicao
                    )
                    result.extend([i.model_dump() for i in insumos])

            await f.write(json.dumps(result, default=custom_converter, indent=6))

        except Exception as error:
            import traceback

            traceback.print_exc()
            print(error)
            print(type(error))
            logger.error(f"An error occurred: {error}")


if __name__ == "__main__":
    asyncio.run(download_insumos_or_compositions(filename='teste', ano='2024'))