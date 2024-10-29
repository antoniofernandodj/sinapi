from math import ceil
from typing import Annotated, List, Optional, Set
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
    TabelasResponse,
    MesesResponse,
    Mes,
)


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_credentials=True,
    allow_methods=["*"],
)


@app.get("/meses", response_model=MesesResponse)
def read_meses(session: Session = Depends(get_db)) -> MesesResponse:

    meses: Set[Mes] = set()
    tabelas: List[Tabela] = session.query(Tabela).all()

    for t in tabelas:
        if not isinstance(t.ano, int) or not isinstance(t.mes, int):
            raise TypeError

        mes = Mes(mes=t.mes, ano=t.ano)
        meses.add(mes)

    return MesesResponse(
        meses=sorted(list(meses), key=lambda mes: str(mes.ano) + "/" + str(mes.mes))
    )


@app.get("/tabelas", response_model=TabelasResponse)
def read_tabelas(session: Session = Depends(get_db)):

    tabelas = session.query(Tabela).all()

    return TabelasResponse(tabelas=[tabela.to_pydantic() for tabela in tabelas])


@app.get("/estados", response_model=EstadosResponse)
def read_estados(session: Session = Depends(get_db)):

    estados = session.query(Estado).all()

    return EstadosResponse(estados=[estado.to_pydantic() for estado in estados])


@app.get("/insumos", response_model=InsumosComposicoesResponse)
def read_insumos(
    page: int = 1,
    limit: Annotated[int, Query(lt=200)] = 10,
    session: Session = Depends(get_db),
    description: Annotated[Optional[str], Query(max_length=200)] = None,
    codigo: Optional[str] = None,
    id: Optional[int] = None,
    id_tabela: Optional[int] = None,
    id_classe: Optional[int] = None,
):

    Table = InsumoTabela
    payload: List[InsumoTabela]

    offset = (page - 1) * limit
    total_count = session.query(Table).count()
    total_pages = ceil(total_count / limit)

    query = session.query(Table)
    if id:
        query = query.filter_by(id=id)

    if codigo:
        query = query.filter_by(codigo=codigo)

    if description:
        query = query.filter(Table.nome.like(f"%{description}%"))

    if id_tabela:
        query = query.filter_by(id_tabela=id_tabela)

    if id_classe:
        query = query.filter_by(id_classe=id_classe)

    query = query.order_by(Table.id).offset(offset).limit(limit)

    result_count = query.count()
    payload = query.all()
    payload_response = mount_insumo_composicao_response(session, payload)

    return InsumosComposicoesResponse(
        payload=payload_response,
        total_rows=total_count,
        total_pages=total_pages,
        current_page=page,
        result_count=result_count,
    )


@app.get("/composicoes", response_model=InsumosComposicoesResponse)
def read_composicoes(
    page: int = 1,
    limit: Annotated[int, Query(lt=200)] = 10,
    db: Session = Depends(get_db),
    description: Annotated[Optional[str], Query(max_length=200)] = None,
    codigo: Optional[str] = None,
    id: Optional[int] = None,
    id_tabela: Optional[int] = None,
    id_classe: Optional[int] = None,
):

    Table = ComposicaoTabela
    payload: List[ComposicaoTabela]

    offset = (page - 1) * limit
    total_count = db.query(Table).count()
    total_pages = ceil(total_count / limit)

    query = db.query(Table)
    if id:
        query = query.filter_by(id=id)

    if codigo:
        query = query.filter_by(codigo=codigo)

    if description:
        query = query.filter(Table.nome.like(f"%{description}%"))

    if id_tabela:
        query = query.filter_by(id_tabela=id_tabela)

    if id_classe:
        query = query.filter_by(id_classe=id_classe)

    query = query.order_by(Table.id).offset(offset).limit(limit)

    result_count = query.count()
    payload = query.all()
    payload_response = mount_insumo_composicao_response(db, payload)

    return InsumosComposicoesResponse(
        payload=payload_response,
        total_rows=total_count,
        total_pages=total_pages,
        current_page=page,
        result_count=result_count,
    )
