import logging
import sys
import pathlib
from datetime import date

from typing import Annotated, Any, List, Optional, Sequence, Set
from fastapi import FastAPI, Depends, Query, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Query as SQLQuery, selectinload
from pymysql.err import OperationalError

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))


from entrypoint.service import (
    ClassesService,
    EstadosService,
    InsumoComposicaoTabelaService,
    MesesService,
    TabelasService,
)

from sinapi.api.schema import InsumoComposicaoTabelaResponse

from entrypoint.utils import (
    # mount_one_insumo_composicao_response,
    get_db,
    get_async_db,
)
from sinapi.models import (
    # ComposicaoTabela,
    ComposicaoItem,
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



logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)



@app.exception_handler(OperationalError)
async def operational_error_handler(request: Request, exc: OperationalError):
    logger.error(f"Erro operacional no banco de dados: {exc}")

    return JSONResponse(
        status_code=500,
        content={
            "msg": f"Erro interno do servidor: Falha na conexão com o banco de dados: {exc}"
        },
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_credentials=True,
    allow_methods=["*"],
)


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


@app.get("/async/estados/composicoes")
async def read_composicoes_do_estado_async(
    session: AsyncSession = Depends(get_async_db),
    codigo: Optional[int] = None,
    id_composicao: Optional[int] = None,
):

    stmt = select(Estado)

    estados_execution_result = await session.execute(stmt)
    estados = estados_execution_result.scalars().all()

    response = {}
    for estado in estados:

        response[estado.nome] = []
        composicoes_do_estado: List[Any] = response[estado.nome]

        stmt = select(Tabela).filter_by(id_estado=estado.id)
        tabelas_execution_result = await session.execute(stmt)
        tabelas = tabelas_execution_result.scalars().all()

        for tabela in tabelas:

            stmt = select(InsumoComposicaoTabela).filter_by(id_tabela=tabela.id)
            if codigo:
                stmt = stmt.filter_by(codigo=codigo)
            if id_composicao:
                stmt = stmt.filter_by(id=id_composicao)

            stmt = stmt.options(
                selectinload(InsumoComposicaoTabela.itens_de_composicao).options(
                    selectinload(ComposicaoItem.insumo_item)
                )
            )

            composicao_execution_result = await session.execute(stmt)
            composicao = composicao_execution_result.scalar()
            if composicao is None:
                continue

            result = composicao.to_pydantic()
            composicoes_do_estado.append(result.model_dump())  # type: ignore

        if len(composicoes_do_estado) == 0:
            del response[estado.nome]

    return response


#############################################################################


@app.get("/insumo-composicao/", response_model=InsumosComposicoesTabelaResponse)
async def async_read_insumo_composicao(
    page: int = 1,
    order_by: Optional[str] = None,
    limit: Annotated[int, Query(lt=200)] = 10,
    descricao: Annotated[Optional[str], Query(max_length=200)] = None,
    codigo: Optional[str] = None,
    id: Optional[int] = None,
    id_tabela: Optional[int] = None,
    id_classe: Optional[int] = None,
    session: AsyncSession = Depends(get_async_db),
    composicao: Optional[bool] = None,
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


@app.get("/insumo-composicao/{id}", response_model=InsumoComposicaoTabelaResponse)
async def async_read_insumo_composicao_by_id(
    id: int, session: Session = Depends(get_async_db)
):
    service = InsumoComposicaoTabelaService(session=session)
    response = await service.read_one_insumo_composicao_by_id_async(id)
    if response is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return response


@app.get("/meses", response_model=MesesResponse)
async def async_read_meses(
    session: AsyncSession = Depends(get_async_db),
) -> MesesResponse:
    meses_services = MesesService(session)
    return await meses_services.read_meses()


@app.get("/tabelas", response_model=TabelasResponse)
async def async_read_tabelas(
    mes_ano: date,
    id_estado: Optional[int] = None,
    session: AsyncSession = Depends(get_async_db),
):
    tabelas_service = TabelasService(session)
    return await tabelas_service.read_tabelas(mes_ano, id_estado)


@app.get("/estados", response_model=EstadosResponse)
async def async_read_estados(session: AsyncSession = Depends(get_async_db)):
    service = EstadosService(session)
    return await service.read_all()


@app.get("/classes", response_model=ClassesResponse)
async def async_read_classes(session: AsyncSession = Depends(get_async_db)):
    service = ClassesService(session)
    return await service.read_all()
