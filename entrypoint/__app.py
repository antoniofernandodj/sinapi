import sys
import pathlib
from datetime import date

from typing import Annotated, Any, List, Optional, Set
from fastapi import FastAPI, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Query as SQLQuery

from sqlalchemy.ext.asyncio import AsyncSession

sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))


from entrypoint.service import (
    ClassesService,
    EstadosService,
    InsumoComposicaoTabelaService,
    MesesService,
    TabelasService
)

from sinapi.api.schema import InsumoComposicaoTabelaResponse

from entrypoint.utils import (
    # mount_one_insumo_composicao_response,
    get_db, get_async_db
)
from sinapi.models import (
    # ComposicaoTabela,
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

    service = InsumoComposicaoTabelaService(session=session)

    return service.read_insumo_composicao(
        composicao=composicao,
        codigo=codigo,
        descricao=descricao,
        id_tabela=id_tabela,
        id_classe=id_classe,
        order_by=order_by,
        page=page,
        limit=limit,
    )


@app.get("/insumo-composicao/{id}", response_model=InsumoComposicaoTabelaResponse)
def read_insumo_composicao_by_id(id: int, session: Session = Depends(get_db)):

    service = InsumoComposicaoTabelaService(session=session)

    response = service.read_one_insummo_composicao_by_id(id)

    if response is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return response


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

    query: SQLQuery = session.query(Tabela)

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

            query = session.query(InsumoComposicaoTabela).filter_by(id_tabela=tabela.id)
            if codigo:
                query = query.filter_by(codigo=codigo)
            if id_composicao:
                query = query.filter_by(id=id_composicao)

            composicao: Optional[InsumoComposicaoTabela] = query.first()
            if composicao is None:
                continue

            result = composicao.to_pydantic()
            composicoes_do_estado.append(result.model_dump())  # type: ignore

        if len(composicoes_do_estado) == 0:
            del response[estado.nome]

    return response



#############################################################################



@app.get("/async/insumo-composicao/", response_model=InsumosComposicoesTabelaResponse)
async def async_read_insumo_composicao(
    composicao: bool,
    page: int = 1,
    order_by: Optional[str] = None,
    limit: Annotated[int, Query(lt=200)] = 10,
    descricao: Annotated[Optional[str], Query(max_length=200)] = None,
    codigo: Optional[str] = None,
    id: Optional[int] = None,
    id_tabela: Optional[int] = None,
    id_classe: Optional[int] = None,
    session: AsyncSession = Depends(get_async_db),
):

    service = InsumoComposicaoTabelaService(session=session)

    return await service.read_insumo_composicao_async(
        composicao=composicao,
        codigo=codigo,
        descricao=descricao,
        id_tabela=id_tabela,
        id_classe=id_classe,
        id=id,
        order_by=order_by,
        page=page,
        limit=limit,
    )


@app.get("/async/insumo-composicao/{id}", response_model=InsumoComposicaoTabelaResponse)
async def async_read_insumo_composicao_by_id(id: int, session: Session = Depends(get_async_db)):
    service = InsumoComposicaoTabelaService(session=session)
    response = service.read_one_insummo_composicao_by_id(id)
    if response is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return response


@app.get("/async/meses", response_model=MesesResponse)
async def async_read_meses(session: AsyncSession = Depends(get_async_db)) -> MesesResponse:
    meses_services = MesesService(session)
    return await meses_services.read_meses()


@app.get("/async/tabelas", response_model=TabelasResponse)
async def async_read_tabelas(
    mes_ano: Optional[date] = None,
    id_estado: Optional[int] = None,
    session: AsyncSession = Depends(get_async_db),
):
    if mes_ano is None:
        raise HTTPException(status_code=400, detail="")
    
    tabelas_service = TabelasService(session)
    return await tabelas_service.read_tabelas(mes_ano, id_estado)


@app.get("/async/estados", response_model=EstadosResponse)
async def async_read_estados(session: AsyncSession = Depends(get_async_db)):
    service = EstadosService(session)
    return await service.read_all()


@app.get("/async/classes", response_model=ClassesResponse)
async def async_read_classes(session: AsyncSession = Depends(get_async_db)):
    service = ClassesService(session)
    return service.read_all()

