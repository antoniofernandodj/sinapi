from typing import List
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from fastapi.middleware.cors import CORSMiddleware

import sys
import pathlib

sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))


from entrypoint.utils import get_db, mount_insumo_composicao_response
from sinapi.models import ComposicaoTabela, InsumoTabela

from entrypoint.schema import InsumosResponse, ComposicaoResponse


app = FastAPI()

app.add_middleware(
    CORSMiddleware(
        app=app,
        allow_origins=["*"],
        allow_headers=["*"],
        allow_credentials=True,
        allow_methods=["*"],
    )
)


@app.get("/insumos", response_model=InsumosResponse)
def read_insumos(page: int = 1, limit: int = 10, session: Session = Depends(get_db)):
    offset = (page - 1) * limit
    count = session.query(InsumoTabela).count()

    insumos: List[InsumoTabela] = (
        session.query(InsumoTabela)
        .order_by(InsumoTabela.id)
        .offset(offset)
        .limit(limit)
        .all()
    )
    insumos_response = mount_insumo_composicao_response(session, insumos)
    return InsumosResponse(insumos=insumos_response, total_rows=count)


@app.get("/composicoes", response_model=ComposicaoResponse)
def read_composicoes(page: int = 1, limit: int = 10, db: Session = Depends(get_db)):
    offset = (page - 1) * limit
    count = db.query(InsumoTabela).count()
    composicoes: List[ComposicaoTabela] = (
        db.query(ComposicaoTabela)
        .order_by(ComposicaoTabela.id)
        .offset(offset)
        .limit(limit)
        .all()
    )
    composicoes_response = mount_insumo_composicao_response(db, composicoes)
    return ComposicaoResponse(composicoes=composicoes_response, total_rows=count)
