from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

import sys
import pathlib

sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))


from sinapi.models import (
    Classe,
    ComposicaoTabela,
    Estado,
    InsumoComposicao,
    InsumoTabela,
    Tabela,
    Unidade,
)
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


@app.get("/insumos", response_model=InsumosResponse)
def read_insumos(page: int = 1, limit: int = 10, db: Session = Depends(get_db)):

    offset = (page - 1) * limit

    insumos: List[InsumoTabela] = (
        db.query(InsumoTabela).offset(offset).limit(limit).all()
    )

    insumos_response = []
    for insumo in insumos:
        insumos_composicoes = (
            db.query(InsumoComposicao).filter_by(id_insumo=insumo.id).all()
        )

        tabela: Optional[Tabela] = (
            db.query(Tabela).filter_by(id_tabela=insumo.id_tabela).first()
        )
        classe: Optional[Classe] = (
            db.query(Classe).filter_by(id_classe=insumo.id_classe).first()
        )
        unidade: Optional[Classe] = (
            db.query(Unidade).filter_by(id_unidade=insumo.id_unidade).first()
        )

        insumos_composicoes = (
            db.query(InsumoComposicao).filter_by(id_insumo=insumo.id).all()
        )

        insumo_response = insumo.to_pydantic()

        insumo_response.tabela = tabela.to_pydantic() if tabela else None
        insumo_response.unidade = unidade.to_pydantic() if unidade else None
        insumo_response.classe = classe.to_pydantic() if classe else None

        insumo_response.insumosComposicoes = [
            ic.to_pydantic() for ic in insumos_composicoes
        ]

        insumos_response.append(insumo_response)

    return InsumosResponse(insumos=insumos_response)


class ComposicaoResponse(BaseModel):
    composicoes: List[InsumosResponseItem]


@app.get("/composicoes", response_model=ComposicaoResponse)
def read_composicoes(page: int = 1, limit: int = 10, db: Session = Depends(get_db)):

    offset = (page - 1) * limit

    composicoes: List[ComposicaoTabela] = (
        db.query(ComposicaoTabela).offset(offset).limit(limit).all()
    )

    composicoes_response = []
    for comp in composicoes:
        insumos_composicoes = (
            db.query(InsumoComposicao).filter_by(id_composicao=comp.id).all()
        )
        comp_response = comp.to_pydantic()
        comp_response.insumosComposicoes = [
            ic.to_pydantic() for ic in insumos_composicoes
        ]
        composicoes_response.append(comp_response)

    return ComposicaoResponse(composicoes=composicoes_response)
