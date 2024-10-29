from datetime import date
from math import ceil
from typing import Annotated, List, Optional, Set
from fastapi import FastAPI, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Query as SQLQuery
from copy import deepcopy


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
def read_tabelas(
    mes_ano: Optional[date] = None,
    id_estado: Optional[int] = None,
    session: Session = Depends(get_db),
):

    print({"q": [mes_ano, id_estado]})

    if mes_ano is None:
        raise HTTPException(status_code=400, detail="")

    query = session.query(Tabela)

    if mes_ano:
        query = query.filter_by(ano=mes_ano.year, mes=mes_ano.month)

    if id_estado:
        query = query.filter_by(id_estado=id_estado)

    tabelas: List[Tabela] = query.all()

    response = TabelasResponse(tabelas=[tabela.to_pydantic() for tabela in tabelas])

    return response


@app.get("/estados", response_model=EstadosResponse)
def read_estados(session: Session = Depends(get_db)):

    estados = session.query(Estado).all()

    return EstadosResponse(estados=[estado.to_pydantic() for estado in estados])


@app.get("/insumos", response_model=InsumosComposicoesResponse)
def read_insumos(
    page: int = 1,
    limit: Annotated[int, Query(lt=200)] = 10,
    session: Session = Depends(get_db),
    descricao: Annotated[Optional[str], Query(max_length=200)] = None,
    codigo: Optional[str] = None,
    id: Optional[int] = None,
    id_tabela: Optional[int] = None,
    id_classe: Optional[int] = None,
):

    Table = InsumoTabela
    payload: List[InsumoTabela]

    offset = (page - 1) * limit

    query: SQLQuery = session.query(Table)
    if id:
        query = query.filter_by(id=id)
    if codigo:
        query = query.filter_by(codigo=codigo)
    if descricao:
        query = query.filter(Table.nome.like(f"%{descricao}%"))
    if id_tabela:
        query = query.filter_by(id_tabela=id_tabela)
    if id_classe:
        query = query.filter_by(id_classe=id_classe)

    result_count = query.count()
    total_pages = ceil(result_count / limit)

    payload = query.order_by(Table.id).offset(offset).limit(limit).all()
    payload_response = mount_insumo_composicao_response(session, payload)

    return InsumosComposicoesResponse(
        payload=payload_response,
        total_pages=total_pages,
        current_page=page,
        result_count=result_count,
    )


@app.get("/composicoes", response_model=InsumosComposicoesResponse)
def read_composicoes(
    page: int = 1,
    limit: Annotated[int, Query(lt=200)] = 10,
    session: Session = Depends(get_db),
    description: Annotated[Optional[str], Query(max_length=200)] = None,
    codigo: Optional[str] = None,
    id: Optional[int] = None,
    id_tabela: Optional[int] = None,
    id_classe: Optional[int] = None,
):

    Table = ComposicaoTabela
    payload: List[ComposicaoTabela]

    offset = (page - 1) * limit
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

    result_count = query.count()
    total_pages = ceil(result_count / limit)

    payload = query.order_by(Table.id).offset(offset).limit(limit).all()
    payload_response = mount_insumo_composicao_response(session, payload)

    return InsumosComposicoesResponse(
        payload=payload_response,
        total_pages=total_pages,
        current_page=page,
        result_count=result_count,
    )
