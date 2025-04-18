from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel
from sniffio import current_async_library
from sinapi.api.schema import (
    EstadoResponseItem,
    InsumoComposicaoTabelaResponse,
    InsumosResponseItem,
    InsumosResponseTabela,
    InsumosResponseClasse,
    InsumosResponseUnidade,
)


class InsumosComposicoesResponse(BaseModel):
    payload: List[InsumosResponseItem]
    total_pages: int
    current_page: int
    result_count: int


class EstadosResponse(BaseModel):
    estados: List[EstadoResponseItem]


class ClassesResponse(BaseModel):
    classes: List[InsumosResponseClasse]


class TabelasResponse(BaseModel):
    tabelas: List[InsumosResponseTabela]


class Mes(BaseModel):
    mes: int
    ano: int

    def __eq__(self, other):
        return (
            isinstance(other, Mes) and self.mes == other.mes and self.ano == other.ano
        )

    def __hash__(self):
        return hash((self.mes, self.ano))


class MesesResponse(BaseModel):
    meses: List[Mes]


class InsumosComposicoesTabelaResponse(BaseModel):
    payload: List[InsumoComposicaoTabelaResponse]
    total_pages: int
    result_count: int


class InsumosResponseUnidades(BaseModel):
    total_pages: int
    result_count: int
    payload: List[InsumosResponseUnidade]