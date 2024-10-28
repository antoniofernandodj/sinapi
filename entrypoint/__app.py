from math import ceil
from typing import Annotated, List, Optional
from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

import sys
import pathlib

sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))


from entrypoint.utils import get_db, mount_insumo_composicao_response
from sinapi.models import ComposicaoTabela, InsumoTabela, Estado, Tabela

from entrypoint.schema import (
    InsumosComposicoesResponse,
    EstadosResponse,
    TabelasResponse
)


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_credentials=True,
    allow_methods=["*"],
)


@app.get("/tabelas", response_model=TabelasResponse)
def read_tabelas(session: Session = Depends(get_db)):

    tabelas = session.query(Tabela).all()

    return TabelasResponse(
        tabelas=[
            tabela.to_pydantic() for tabela in tabelas
        ]
    )


@app.get("/estados", response_model=EstadosResponse)
def read_estados(session: Session = Depends(get_db)):

    estados = session.query(Estado).all()

    return EstadosResponse(
        estados=[
            estado.to_pydantic() for estado in estados
        ]
    )


@app.get("/insumos", response_model=InsumosComposicoesResponse)
def read_insumos(
    page: int = 1,
    limit: Annotated[int, Query(lt=200)] = 10,
    session: Session = Depends(get_db),
    description: Annotated[Optional[str], Query(max_length=200)] = None,
    codigo: Optional[str] = None
):
    offset = (page - 1) * limit
    total_count = session.query(InsumoTabela).count()
    total_pages = ceil(total_count / limit)

    query = session.query(InsumoTabela)

    if codigo:
        query = query.filter_by(codigo=codigo)

    elif description:
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
    return InsumosComposicoesResponse(
        payload=insumos_response,
        total_rows=total_count,
        total_pages=total_pages,
        current_page=page,
        result_count=result_count
    )


@app.get("/composicoes", response_model=InsumosComposicoesResponse)
def read_composicoes(
    page: int = 1,
    limit: Annotated[int, Query(lt=200)] = 10,
    db: Session = Depends(get_db),
    description: Annotated[Optional[str], Query(max_length=200)] = None,
    codigo: Optional[str] = None
):
    offset = (page - 1) * limit
    total_count = db.query(ComposicaoTabela).count()
    total_pages = ceil(total_count / limit)

    query = db.query(ComposicaoTabela)
    if codigo:
        query = query.filter_by(codigo=codigo)

    elif description:
        query = query.filter(InsumoTabela.nome.like(f'%{description}%'))

    query = (
        query
        .order_by(ComposicaoTabela.id)
        .offset(offset)
        .limit(limit)
    )

    result_count = query.count()
    composicoes: List[ComposicaoTabela] = query.all()
    composicoes_response = mount_insumo_composicao_response(db, composicoes)

    return InsumosComposicoesResponse(
        payload=composicoes_response,
        total_rows=total_count,
        total_pages=total_pages,
        current_page=page,
        result_count=result_count,
    )
