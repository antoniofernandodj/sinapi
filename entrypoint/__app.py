from math import ceil
from typing import Annotated, List, Optional
from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from fastapi.openapi.utils import get_openapi

from fastapi.middleware.cors import CORSMiddleware

import sys
import pathlib

sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))


from entrypoint.utils import get_db, mount_insumo_composicao_response
from sinapi.models import ComposicaoTabela, InsumoTabela

from entrypoint.schema import InsumosResponse, ComposicaoResponse


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_credentials=True,
    allow_methods=["*"],
)


@app.get("/insumos", response_model=InsumosResponse)
def read_insumos(
    page: int = 1,
    limit: Annotated[int, Query(lt=200)] = 10,
    session: Session = Depends(get_db),
    description: Annotated[Optional[str], Query(max_length=200)] = None,
):
    offset = (page - 1) * limit
    total_count = session.query(InsumoTabela).count()
    total_pages = ceil(total_count / limit)

    query = session.query(InsumoTabela)
    if description:
        query = query.filter(InsumoTabela.nome.like(f'%{description}%'))

    query = (
        query
        .order_by(InsumoTabela.id)
        .offset(offset)
        .limit(limit)
    )

    result_count = query.count()

    insumos: List[InsumoTabela] = query.all()

    insumos_response = mount_insumo_composicao_response(session, insumos)
    return InsumosResponse(
        insumos=insumos_response,
        total_rows=total_count,
        total_pages=total_pages,
        current_page=page,
        result_count=result_count
    )


@app.get("/composicoes", response_model=ComposicaoResponse)
def read_composicoes(
    page: int = 1,
    limit: Annotated[int, Query(lt=200)] = 10,
    db: Session = Depends(get_db),
    description: Annotated[Optional[str], Query(max_length=200)] = None,
):
    offset = (page - 1) * limit
    total_count = db.query(ComposicaoTabela).count()
    total_pages = ceil(total_count / limit)

    query = db.query(ComposicaoTabela)
    if description:
        query = query.filter(ComposicaoTabela.nome.like(f'%{description}%'))

    query = (
        query
        .order_by(ComposicaoTabela.id)
        .offset(offset)
        .limit(limit)
    )

    result_count = query.count()
    composicoes: List[ComposicaoTabela] = query.all()
    composicoes_response = mount_insumo_composicao_response(db, composicoes)

    return ComposicaoResponse(
        composicoes=composicoes_response,
        total_rows=total_count,
        total_pages=total_pages,
        current_page=page,
        result_count=result_count,
    )
