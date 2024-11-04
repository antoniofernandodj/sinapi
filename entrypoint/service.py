from math import ceil
from typing import Annotated, Optional
from fastapi import Query
from sqlalchemy import asc, desc

from entrypoint.schema import InsumosComposicoesTabelaResponse
from sinapi.models import InsumoComposicaoTabela


class InsumoComposicaoTabelaService:
    def __init__(self, session):
        self.session = session

    def read_one_insummo_composicao_by_id(self, id: int):
        item = self.session.query(InsumoComposicaoTabela).filter_by(id=id).first()

        if not item:
            return None

        return item.to_pydantic()

    def read_insumo_composicao(
        self,
        composicao: bool,
        page: int = 1,
        order_by: Optional[str] = None,
        limit: Annotated[int, Query(lt=200)] = 10,
        descricao: Annotated[Optional[str], Query(max_length=200)] = None,
        codigo: Optional[str] = None,
        id: Optional[int] = None,
        id_tabela: Optional[int] = None,
        id_classe: Optional[int] = None,
    ):
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
