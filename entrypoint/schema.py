from typing import List
from pydantic import BaseModel
from sniffio import current_async_library
from sinapi.api.schema import EstadoResponseItem, InsumosResponseItem, InsumosResponseTabela


class InsumosResponse(BaseModel):
    insumos: List[InsumosResponseItem]
    total_rows: int
    total_pages: int
    current_page: int
    result_count: int


class ComposicaoResponse(BaseModel):
    composicoes: List[InsumosResponseItem]
    total_rows: int
    total_pages: int
    current_page: int
    result_count: int


class EstadosResponse(BaseModel):
    estados: List[EstadoResponseItem]


class TabelasResponse(BaseModel):
    tabelas: List[InsumosResponseTabela]
