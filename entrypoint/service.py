from datetime import date
from math import ceil
from typing import (
    Optional,
    Sequence,
    Set,
    Union
)
from sqlalchemy import Select
from sqlalchemy.sql import (
    asc,
    desc,
    func
)
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import (
    Session,
    selectinload
)

from entrypoint.schema import (
    ClassesResponse,
    EstadosResponse,
    InsumosComposicoesTabelaResponse,
    Mes,
    MesesResponse,
    TabelasResponse,
)

from sinapi.models import (
    Classe,
    ComposicaoItem,
    Estado,
    InsumoComposicaoTabela,
    Tabela,
    Unidade
)

from entrypoint.schema import (
    InsumosResponseUnidades
)


class InsumoComposicaoTabelaService:
    def __init__(self, session):
        self.session: Union[AsyncSession, Session] = session

    def read_one_insumo_composicao_by_id(self, id: int):
        if not isinstance(self.session, Session):
            raise TypeError
        item = self.session.query(InsumoComposicaoTabela).filter_by(id=id).first()
        if not item:
            return None
        return item.to_pydantic()

    async def read_one_insumo_composicao_by_id_async(self, id: int):
        if not isinstance(self.session, AsyncSession):
            raise TypeError

        stmt = (
            select(InsumoComposicaoTabela)
            .options(
                selectinload(InsumoComposicaoTabela.itens_de_composicao).options(
                    selectinload(ComposicaoItem.insumo_item)
                )
            )
            .options(selectinload(InsumoComposicaoTabela.tabela))
            .options(selectinload(InsumoComposicaoTabela.classe))
            .options(selectinload(InsumoComposicaoTabela.unidade))
            .filter_by(id=id)
        )

        composicao_execution_result = await self.session.execute(stmt)
        composicao = composicao_execution_result.scalar()
        if not composicao:
            return None
        return composicao.to_pydantic()

    def read_insumo_composicao(
        self,
        composicao: bool,
        page: int = 1,
        order_by: Optional[str] = None,
        limit: int = 10,
        descricao: Optional[str] = None,
        codigo: Optional[str] = None,
        id: Optional[int] = None,
        id_tabela: Optional[int] = None,
        id_classe: Optional[int] = None,
    ):
        if not isinstance(self.session, Session):
            raise TypeError

        Table = InsumoComposicaoTabela
        offset = (page - 1) * limit

        query = self.session.query(Table)

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
            query = self.apply_order_by(query, Table, order_by)

        result_count = query.count()
        total_pages = ceil(result_count / limit)

        result = query.order_by(Table.id).offset(offset).limit(limit).all()

        return InsumosComposicoesTabelaResponse(
            total_pages=total_pages,
            result_count=result_count,
            payload=[item.to_pydantic() for item in result],
        )

    def apply_order_by(self, query, model, order_by_str):
        if " " in order_by_str:
            column_name, direction = order_by_str.split()
            direction = direction.lower()
        else:
            column_name = order_by_str
            direction = "asc"

        column = getattr(model, column_name, None)
        if column is None:
            raise ValueError(f"Invalid column name: {column_name}")

        if direction == "desc":
            query = query.order_by(desc(column))
        else:
            query = query.order_by(asc(column))

        return query

    async def read_insumo_composicao_async(
        self,
        composicao: Optional[bool],
        page: int = 1,
        order_by: Optional[str] = None,
        limit: int = 10,
        descricao: Optional[str] = None,
        codigo: Optional[str] = None,
        id: Optional[int] = None,
        id_tabela: Optional[int] = None,
        id_classe: Optional[int] = None,
    ):
        if not isinstance(self.session, AsyncSession):
            raise TypeError

        Table = InsumoComposicaoTabela
        offset = (page - 1) * limit

        query = select(Table)
        q_count = select(func.count("*")).select_from(Table)

        def compose_query(query):
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
                query = self.apply_order_by(query, Table, order_by)

            return query

        query = compose_query(query)
        q_count = compose_query(q_count)

        r_count = await self.session.execute(q_count)
        r = await self.session.execute(
            query.order_by(Table.id)
            .options(
                selectinload(Table.itens_de_composicao).options(
                    selectinload(ComposicaoItem.insumo_item)
                )
            )
            .options(selectinload(Table.tabela))
            .options(selectinload(Table.classe))
            .options(selectinload(Table.unidade))
            .offset(offset)
            .limit(limit)
        )

        result_count = r_count.scalar_one()
        total_pages = ceil(result_count / limit)

        result = r.scalars().all()

        return InsumosComposicoesTabelaResponse(
            total_pages=total_pages,
            result_count=result_count,
            payload=[item.to_pydantic() for item in result],
        )


    async def read_insumo_composicao_using_like_async(
        self,
        composicao: bool,
        limit: int,
        like_param: Optional[str] = None,
    ):
        if not isinstance(self.session, AsyncSession):
            raise TypeError

        Table = InsumoComposicaoTabela

        query = select(Table)

        def compose_query(query: Select):
            if composicao:
                query = query.filter_by(composicao=composicao)
            if like_param:
                query = query.filter(Table.nome.like(f"%{like_param}%"))

            return query.limit(limit)

        query = compose_query(query)

    
        r = await (
            self.session.execute(
                query.order_by(Table.id)
                .options(
                    selectinload(Table.itens_de_composicao)
                    .options(
                        selectinload(ComposicaoItem.insumo_item)
                    )
                )
                .options(selectinload(Table.tabela))
                .options(selectinload(Table.classe))
                .options(selectinload(Table.unidade))
            )
        )

        result = r.scalars().all()

        return InsumosComposicoesTabelaResponse(
            total_pages=0,
            result_count=0,
            payload=[item.to_pydantic() for item in result],
        )
    


class MesesService:
    def __init__(self, session):
        self.session = session

    async def read_meses(self):
        meses: Set[Mes] = set()
        query = select(Tabela)

        tabelas = (await self.session.execute(query)).scalars().all()

        for t in tabelas:
            if not isinstance(t.ano, int) or not isinstance(t.mes, int):
                raise TypeError

            mes = Mes(mes=t.mes, ano=t.ano)
            meses.add(mes)

        return MesesResponse(
            meses=sorted(list(meses), key=lambda mes: str(mes.ano) + "/" + str(mes.mes))
        )


class TabelasService:
    def __init__(self, session):
        self.session = session

    async def read_tabelas(self, mes_ano: date, id_estado: Optional[int] = None):
        query = select(Tabela)
        query = query.filter_by(ano=mes_ano.year, mes=mes_ano.month)
        query = query.filter_by(id_estado=id_estado) if id_estado else query
        tabelas: Sequence[Tabela] = (await self.session.execute(query)).scalars().all()
        response = TabelasResponse(tabelas=[tabela.to_pydantic() for tabela in tabelas])
        return response


class EstadosService:
    def __init__(self, session):
        self.session = session

    async def read_all(self):
        query = select(Estado)
        estados = (await self.session.execute(query)).scalars().all()
        return EstadosResponse(estados=[estado.to_pydantic() for estado in estados])


class ClassesService:
    def __init__(self, session):
        self.session = session

    async def read_all(self):
        query = select(Classe)
        classes = (await self.session.execute(query)).scalars().all()
        return ClassesResponse(classes=[classe.to_pydantic() for classe in classes])


class UnidadesService:
    def __init__(self, session):
        self.session: Union[AsyncSession, Session] = session

    def read_all(
        self,
        page: int = 1,
        limit: int = 20,
        order_by: Optional[str] = None,
        nome: Optional[str] = None,
        excluido: Optional[bool] = None,
    ):
        if not isinstance(self.session, Session):
            raise TypeError

        offset = (page - 1) * limit
        query = self.session.query(Unidade)

        if nome:
            query = query.filter(Unidade.nome.ilike(f"%{nome}%"))
        if excluido is not None:
            query = query.filter(Unidade.excluido == excluido)
        if order_by:
            query = self.apply_order_by(query, Unidade, order_by)

        total = query.count()
        total_pages = ceil(total / limit)

        result = query.offset(offset).limit(limit).all()
        payload = [u.to_pydantic() for u in result]

        return InsumosResponseUnidades(
            total_pages=total_pages,
            result_count=total,
            payload=payload
        )

    async def read_all_async(
        self,
        page: int = 1,
        limit: int = 20,
        order_by: Optional[str] = None,
        nome: Optional[str] = None,
        excluido: Optional[bool] = None,
    ):
        if not isinstance(self.session, AsyncSession):
            raise TypeError

        offset = (page - 1) * limit
        query = select(Unidade)
        q_count = select(func.count()).select_from(Unidade)

        def compose(q):
            if nome:
                q = q.filter(Unidade.nome.ilike(f"%{nome}%"))
            if excluido is not None:
                q = q.filter(Unidade.excluido == excluido)
            if order_by:
                q = self.apply_order_by(q, Unidade, order_by)
            return q

        query = compose(query)
        q_count = compose(q_count)

        r_count = await self.session.execute(q_count)
        result_count = r_count.scalar_one()

        r = await self.session.execute(
            query.order_by(Unidade.id).offset(offset).limit(limit)
        )
        unidades = r.scalars().all()

        return InsumosResponseUnidades(
            total_pages=ceil(result_count / limit),
            result_count=result_count,
            payload=[u.to_pydantic() for u in unidades]
        )

    def apply_order_by(self, query, model, order_by_str):
        if " " in order_by_str:
            column_name, direction = order_by_str.split()
        else:
            column_name, direction = order_by_str, "asc"

        column = getattr(model, column_name, None)
        if column is None:
            raise ValueError(f"Coluna inválida: {column_name}")

        return query.order_by(desc(column) if direction.lower() == "desc" else asc(column))