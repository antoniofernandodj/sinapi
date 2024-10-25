from typing import List
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

import sys
import pathlib

sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))


from entrypoint.utils import get_db, mount_insumo_composicao_response
from sinapi.models import ComposicaoTabela, InsumoTabela

from entrypoint.schema import InsumosResponse, ComposicaoResponse


app = FastAPI()


@app.get("/insumos", response_model=InsumosResponse)
def read_insumos(page: int = 1, limit: int = 10, db: Session = Depends(get_db)):
    offset = (page - 1) * limit
    insumos: List[InsumoTabela] = (
        db.query(InsumoTabela)
        .order_by(InsumoTabela.id)
        .offset(offset)
        .limit(limit)
        .all()
    )
    insumos_response = mount_insumo_composicao_response(db, insumos)
    return InsumosResponse(insumos=insumos_response)


@app.get("/composicoes", response_model=ComposicaoResponse)
def read_composicoes(page: int = 1, limit: int = 10, db: Session = Depends(get_db)):
    offset = (page - 1) * limit
    composicoes: List[ComposicaoTabela] = (
        db.query(ComposicaoTabela)
        .order_by(ComposicaoTabela.id)
        .offset(offset)
        .limit(limit)
        .all()
    )
    composicoes_response = mount_insumo_composicao_response(db, composicoes)
    return ComposicaoResponse(composicoes=composicoes_response)
