from typing import List
from pydantic import BaseModel
from sinapi.api.schema import EstadoResponseItem, InsumosResponseItem


class InsumosResponse(BaseModel):
    insumos: List[InsumosResponseItem]


class ComposicaoResponse(BaseModel):
    composicoes: List[InsumosResponseItem]
