from typing import List
from pydantic import BaseModel
from sinapi.api.schema import EstadoResponseItem, InsumosResponseItem


class InsumosResponse(BaseModel):
    insumos: List[InsumosResponseItem]
    total_rows: int
    total_pages: int


class ComposicaoResponse(BaseModel):
    composicoes: List[InsumosResponseItem]
    total_rows: int
    total_pages: int
