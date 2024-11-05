ID = 16641561
ID2 = 13358074

import asyncio
import sys
import pathlib

sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))

from sinapi.database import ASYNC_DATABASE_INSUMOS_URL2, get_async_session_local
from sinapi.models import InsumoComposicaoTabela, Tabela
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload


AsyncSessionLocal = get_async_session_local(ASYNC_DATABASE_INSUMOS_URL2, echo=False)

async def main():
    FALTANTES = []

    async with AsyncSessionLocal() as session:

        tabelas = set((
            await session.execute(
                select(Tabela).options(selectinload(Tabela.estado))
                )
            )
            .scalars()
            .all()
        )

        for tabela in tabelas:
            query = select(InsumoComposicaoTabela.id).filter_by(id_tabela=tabela.id)
            result = await session.execute(query)
            results = (result.scalars().all())
            if results:
                faltantes = [
                    r for r in range(min(results), max(results) + 1)
                    if r not in results
                ]
                if faltantes:
                    FALTANTES.extend(faltantes)

        FALTANTES = list(set(FALTANTES))
        with open('file.txt', 'w') as f:
            print(FALTANTES, file=f)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())