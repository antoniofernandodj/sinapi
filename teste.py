# import asyncio
# from typing import Any, AsyncGenerator
# from sqlalchemy import select

# try:
#     from sinapi.database import DATABASE_INSUMOS_URL2, get_session_local
#     from sinapi.models import InsumoComposicaoTabela, ComposicaoItem
# except:
#     from database import DATABASE_INSUMOS_URL2, get_session_local
#     from models import InsumoComposicaoTabela, ComposicaoItem


# SessionLocal = get_session_local(DATABASE_INSUMOS_URL2, echo=False)


# with SessionLocal() as session:

#     stmt = select(InsumoComposicaoTabela.id).where(
#         InsumoComposicaoTabela.composicao == True
#     )
#     ids = [row[0] for row in session.execute(stmt)]

#     for id in ids:
#         item = session.query(InsumoComposicaoTabela).filter_by(id=id).first()

#         assert item

#         print(item.id)

#         vinculos = session.query(ComposicaoItem).filter_by(id_insumo=item.id).all()

#         print(vinculos)

#     # print_tree(item)
