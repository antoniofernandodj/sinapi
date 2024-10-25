from typing import List
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

import sys
import pathlib

sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))

from sinapi.models import ComposicaoTabela, Estado, InsumoTabela
from sinapi.database import Session as SessionLocal
from sinapi.api.schema import EstadoResponseItem, InsumosResponseItem
from pydantic import BaseModel

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class InsumosResponse(BaseModel):
    insumos: List[InsumosResponseItem]


@app.get(
    "/insumos",
    response_model=InsumosResponse
)
def read_insumos(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    insumos: List[InsumoTabela] = db.query(InsumoTabela).offset(skip).limit(limit).all()
    print(insumos)

    insumos_response = [insumo.to_pydantic() for insumo in insumos]

    return InsumosResponse(insumos=insumos_response)


# @app.get(
#     "/composicoes",
#     response_model=List[ComposicaoTabela]
# )
# def read_composicoes(
#     skip: int = 0,
#     limit: int = 10,
#     db: Session = Depends(get_db)
# ):
#     composicoes = db.query(ComposicaoTabela).offset(skip).limit(limit).all()
#     return composicoes
