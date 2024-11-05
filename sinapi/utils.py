from contextlib import suppress
from typing import Optional

from sinapi.api.schema import EstadoResponseItem
from sqlalchemy import asc, desc


try:
    from sinapi.api.schema import EstadoResponse
    from sinapi.api import SinapiService
except:
    from api import SinapiService
    from api.schema import EstadoResponse


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
        return estado.uf in ["TO"]
        # return True

    estados_response_items = estados_response.items if estados_response else []
    result = list(filter(filtrar_estados, set(estados_response_items)))

    return sorted(list(result), key=lambda item: item.id)


def apply_order_by(query, model, order_by_str):
    if " " in order_by_str:
        column_name, direction = order_by_str.split()
        direction = direction.lower()
    else:
        column_name = order_by_str
        direction = "asc"

    column = getattr(model, column_name, None)
    if column is None:
        raise ValueError(f"Invalid column name: {column_name}")

    if direction == "desc":
        query = query.order_by(desc(column))
    else:
        query = query.order_by(asc(column))

    return query


if __name__ == "__main__":
    import asyncio

    async def main():
        service = SinapiService(login, senha)
        await get_estados_a_cadastrar(service)

    asyncio.run(main())
