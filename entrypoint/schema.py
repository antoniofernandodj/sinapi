from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel
from sniffio import current_async_library
from sinapi.api.schema import (
    EstadoResponseItem,
    InsumosResponseItem,
    InsumosResponseTabela,
)


class InsumosComposicoesResponse(BaseModel):
    payload: List[InsumosResponseItem]
    total_rows: int
    total_pages: int
    current_page: int
    result_count: int


class EstadosResponse(BaseModel):
    estados: List[EstadoResponseItem]


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


class TabelasQuery(BaseModel):
    mes_ano: Optional[date] = None
    id_estado: Optional[int] = None
