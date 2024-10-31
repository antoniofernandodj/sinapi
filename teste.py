import asyncio
from typing import Any, AsyncGenerator
from sqlalchemy import select

try:
    from sinapi.database import DATABASE_INSUMOS_URL2, get_session_local
    from sinapi.models import InsumoComposicaoTabela, ComposicaoItem
except:
    from database import DATABASE_INSUMOS_URL2, get_session_local  # type: ignore
    from models import InsumoComposicaoTabela, ComposicaoItem  # type: ignore


SessionLocal = get_session_local(DATABASE_INSUMOS_URL2, echo=False)


with SessionLocal() as session:

    T1 = InsumoComposicaoTabela
    stmt = select(T1.id)
    ids = [row[0] for row in session.execute(stmt)]

    for id in ids:
        T2 = InsumoComposicaoTabela
        pai = session.query(T2).filter_by(id=id).first()

        assert pai

        print(f"filhos: {pai.itens_filho}")

        # pai = (
        #     session.query(InsumoComposicaoTabela).filter_by(id=vinculo.id_insumo).all()
        # )

        # filho = (
        #     session.query(InsumoComposicaoTabela)
        #     .filter_by(id=vinculo.id_insumo_item)
        #     .all()
        # )

        # print({"pai": pai, "filho": filho})

    # print_tree(item)
