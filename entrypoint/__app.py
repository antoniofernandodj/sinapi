from datetime import date
from math import ceil
from typing import Annotated, Any, List, Optional, Set
from fastapi import FastAPI, Depends, Query, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Query as SQLQuery
from copy import deepcopy


import sys
import pathlib

from sinapi.api.schema import InsumoComposicaoTabelaResponse, InsumosResponseItem
from sinapi.utils import apply_order_by

sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))


from entrypoint.utils import (
    mount_one_insumo_composicao_response,
    get_db,
)
from sinapi.models import (
    ComposicaoTabela,
    InsumoComposicaoTabela,
    Estado,
    Tabela,
    Classe,
)

from entrypoint.schema import (
    ClassesResponse,
    EstadosResponse,
    InsumosComposicoesTabelaResponse,
    TabelasResponse,
    MesesResponse,
    Mes,
)


app = FastAPI(
    docs_url="/app/sinapi/docs",
    openapi_url="/app/sinapi/openapi.json",
    root_path="/app/sinapi",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_credentials=True,
    allow_methods=["*"],
)


@app.get("/insumo-composicao/", response_model=InsumosComposicoesTabelaResponse)
def read_insumo_composicao(
    composicao: bool,
    page: int = 1,
    order_by: Optional[str] = None,
    limit: Annotated[int, Query(lt=200)] = 10,
    descricao: Annotated[Optional[str], Query(max_length=200)] = None,
    codigo: Optional[str] = None,
    id: Optional[int] = None,
    id_tabela: Optional[int] = None,
    id_classe: Optional[int] = None,
    session: Session = Depends(get_db),
):

    Table = InsumoComposicaoTabela
    offset = (page - 1) * limit

    query = session.query(Table)

    if composicao:
        query = query.filter_by(composicao=composicao)
    if id:
        query = query.filter_by(id=id)
    if codigo:
        query = query.filter_by(codigo=codigo)
    if descricao:
        query = query.filter(Table.nome.like(f"%{descricao}%"))  # type: ignore
    if id_tabela:
        query = query.filter_by(id_tabela=id_tabela)
    if id_classe:
        query = query.filter_by(id_classe=id_classe)
    if order_by:
        query = apply_order_by(query, Table, order_by)

    result_count = query.count()
    total_pages = ceil(result_count / limit)

    result = query.order_by(Table.id).offset(offset).limit(limit).all()

    return InsumosComposicoesTabelaResponse(
        total_pages=total_pages,
        result_count=result_count,
        payload=[item.to_pydantic() for item in result],
    )


@app.get("/insumo-composicao/{id}", response_model=InsumoComposicaoTabelaResponse)
def read_insumo_composicao_by_id(id: int, session: Session = Depends(get_db)):

    item = session.query(InsumoComposicaoTabela).filter_by(id=id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return item.to_pydantic()


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


@app.get("/classes", response_model=ClassesResponse)
def read_classes(session: Session = Depends(get_db)):
    classes: List[Classe] = session.query(Classe).all()
    return ClassesResponse(classes=[classe.to_pydantic() for classe in classes])


# @app.get("/insumos", response_model=InsumosComposicoesResponse)
# def read_insumos(
#     page: int = 1,
#     limit: Annotated[int, Query(lt=200)] = 10,
#     order_by: Optional[str] = None,
#     session: Session = Depends(get_db),
#     descricao: Annotated[Optional[str], Query(max_length=200)] = None,
#     codigo: Optional[str] = None,
#     id: Optional[int] = None,
#     id_tabela: Optional[int] = None,
#     id_classe: Optional[int] = None,
# ):

#     Table = InsumoTabela
#     payload: List[InsumoTabela]

#     offset = (page - 1) * limit

#     query: SQLQuery = session.query(Table)
#     if id:
#         query = query.filter_by(id=id)
#     if codigo:
#         query = query.filter_by(codigo=codigo)
#     if descricao:
#         query = query.filter(Table.nome.like(f"%{descricao}%"))  # type: ignore
#     if id_tabela:
#         query = query.filter_by(id_tabela=id_tabela)
#     if id_classe:
#         query = query.filter_by(id_classe=id_classe)
#     if order_by:
#         query = apply_order_by(query, Table, order_by)

#     result_count = query.count()
#     total_pages = ceil(result_count / limit)

#     payload = query.order_by(Table.id).offset(offset).limit(limit).all()  # type: ignore
#     payload_response = mount_insumo_composicao_response(session, payload)

#     return InsumosComposicoesResponse(
#         payload=payload_response,
#         total_pages=total_pages,
#         current_page=page,
#         result_count=result_count,
#     )


# @app.get("/composicoes", response_model=InsumosComposicoesResponse)
# def read_composicoes(
#     page: int = 1,
#     limit: Annotated[int, Query(lt=200)] = 10,
#     order_by: Optional[str] = None,
#     session: Session = Depends(get_db),
#     descricao: Annotated[Optional[str], Query(max_length=200)] = None,
#     codigo: Optional[str] = None,
#     id: Optional[int] = None,
#     id_tabela: Optional[int] = None,
#     id_classe: Optional[int] = None,
# ):

#     Table = ComposicaoTabela
#     payload: List[ComposicaoTabela]

#     offset = (page - 1) * limit
#     query = session.query(Table)

#     if id:
#         query = query.filter_by(id=id)
#     if codigo:
#         query = query.filter_by(codigo=codigo)
#     if descricao:
#         query = query.filter(Table.nome.like(f"%{descricao}%"))  # type: ignore
#     if id_tabela:
#         query = query.filter_by(id_tabela=id_tabela)
#     if id_classe:
#         query = query.filter_by(id_classe=id_classe)
#     if order_by:
#         query = apply_order_by(query, Table, order_by)

#     result_count = query.count()
#     total_pages = ceil(result_count / limit)

#     payload = query.order_by(Table.id).offset(offset).limit(limit).all()  # type: ignore
#     payload_response = mount_insumo_composicao_response(session, payload)

#     return InsumosComposicoesResponse(
#         payload=payload_response,
#         total_pages=total_pages,
#         current_page=page,
#         result_count=result_count,
#     )


# @app.get("/composicoes/{composicao_id}", response_model=InsumosResponseItem)
# def read_composicao(composicao_id: int, session: Session = Depends(get_db)):

#     composicao: Optional[ComposicaoTabela] = (
#         session.query(ComposicaoTabela).filter_by(id=composicao_id).first()
#     )
#     if not composicao:
#         raise HTTPException(status_code=404, detail="Nenhuma composição encontrada")

#     return mount_one_insumo_composicao_response(composicao, session)


@app.get("/estados/composicoes")
def read_composicoes_do_estado(
    session=Depends(get_db),
    codigo: Optional[int] = None,
    id_composicao: Optional[int] = None,
):

    estados: List[Estado] = session.query(Estado).all()

    response = {}
    for estado in estados:

        response[estado.nome] = []
        composicoes_do_estado: List[Any] = response[estado.nome]

        query = session.query(Tabela).filter_by(id_estado=estado.id)
        tabelas: List[Tabela] = query.all()

        for tabela in tabelas:

            query = session.query(ComposicaoTabela).filter_by(id_tabela=tabela.id)

            if codigo:
                query = query.filter_by(codigo=codigo)

            if id_composicao:
                query = query.filter_by(id=id_composicao)

            composicao: Optional[ComposicaoTabela] = query.first()
            result = mount_one_insumo_composicao_response(composicao, session)

            if composicao is None:
                continue

            composicoes_do_estado.append(result.model_dump())  # type: ignore

        if len(composicoes_do_estado) == 0:
            del response[estado.nome]

    return response
