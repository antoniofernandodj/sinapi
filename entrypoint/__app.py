from typing import List
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

import sys
import pathlib

sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))

from sinapi.models import ComposicaoTabela, Estado, InsumoComposicao, InsumoTabela
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
    insumos: List[InsumoTabela] = (
        db.query(InsumoTabela)
        .offset(skip)
        .limit(limit)
        .all()
    )

    insumos_response = []
    for insumo in insumos:
        insumos_composicoes = db.query(InsumoComposicao).filter_by(id_insumo=insumo.id).all()
        insumo_response = insumo.to_pydantic()
        insumo_response.insumosComposicoes = [
            ic.to_pydantic() for ic in insumos_composicoes
        ]
        insumos_response.append(insumo_response)

    return InsumosResponse(insumos=insumos_response)


@app.get(
    "/composicoes",
    response_model=List[ComposicaoTabela]
)
def read_composicoes(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    composicoes: List[ComposicaoTabela] = (
        db.query(ComposicaoTabela)
        .offset(skip)
        .limit(limit)
        .all()
    )

    composicoes_response = []
    for comp in composicoes:
        insumos_composicoes = db.query(InsumoComposicao).filter_by(id_composicao=comp.id).all()
        comp_response = comp.to_pydantic()
        comp_response.insumosComposicoes = [
            ic.to_pydantic() for ic in insumos_composicoes
        ]
        insumos_response.append(insumo_response)

    return InsumosResponse(insumos=insumos_response)