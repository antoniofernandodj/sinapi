from datetime import datetime
import logging
from pathlib import Path
from typing import Any, Dict, List
from api import SinapiService
import aiofiles
import json


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
                page=None,  # page=1,
                limit=None  # limit=20
            )

            result: List[Dict[str, Any]] = []
            for estado_response in estados_response.items:
                uf = estado_response.uf
                meses = await service.meses_importados(
                    tipo_tabela="SINAPI", uf=uf, ano=ano
                )
                for mes in meses:
                    insumos = await service.insumos(
                        ano=ano,
                        mes=mes.value,
                        uf=uf,
                        # page=1,
                        limit=50,
                        composicao=composicao,
                    )
                    # print(insumos)
                    result.extend([o.model_dump() for o in insumos.items])

            await f.write(json.dumps(result, default=custom_converter, indent=6))

        except Exception as error:
            import traceback

            traceback.print_exc()
            print(error)
            print(type(error))
            logger.error(f"An error occurred: {error}")
