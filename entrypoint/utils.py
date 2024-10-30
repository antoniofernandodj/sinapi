from typing import Optional
from sinapi.database import Session as SessionLocal
from sqlalchemy.orm import Session
from sinapi.models import (
    Classe,
    ComposicaoTabela,
    InsumoComposicao,
    InsumoComposicaoResponse,
    InsumoItem,
    InsumoTabela,
    Tabela,
    Unidade,
)


def mount_one_insumo_composicao_response(insumo_composicao, db: Session):
    if not isinstance(insumo_composicao, (InsumoTabela, ComposicaoTabela)):
        return

    response = insumo_composicao.to_pydantic()
    tabela = db.query(Tabela).filter_by(id=insumo_composicao.id_tabela).first()
    classe = db.query(Classe).filter_by(id=insumo_composicao.id_classe).first()
    unidade = db.query(Unidade).filter_by(id=insumo_composicao.id_unidade).first()

    if not isinstance(tabela, (Tabela, type(None))):
        raise TypeError
    if not isinstance(unidade, (Unidade, type(None))):
        raise TypeError
    if not isinstance(classe, (Classe, type(None))):
        raise TypeError

    response.tabela = tabela.to_pydantic() if tabela else None
    response.unidade = unidade.to_pydantic() if unidade else None
    response.classe = classe.to_pydantic() if classe else None

    response.insumosComposicoes = []

    if isinstance(insumo_composicao, ComposicaoTabela):
        query_all = (
            db.query(InsumoComposicao)
            .filter_by(id_composicao=insumo_composicao.id)
            .all()
        )
    else:
        query_all = (
            db.query(InsumoComposicao).filter_by(id_insumo=insumo_composicao.id).all()
        )
    for ic in query_all:
        if not isinstance(ic, InsumoComposicao):
            continue
        insumo_item: Optional[InsumoItem] = (
            db.query(InsumoItem).filter_by(id=ic.id_insumo_item).first()
        )

        if insumo_item is None:
            continue

        ic_response: InsumoComposicaoResponse = ic.to_pydantic(
            insumo_item.to_pydantic()
        )
        response.insumosComposicoes.append(ic_response)

    return response


def mount_insumo_composicao_response(db: Session, insumos_composicoes):
    result = []
    for obj in insumos_composicoes:
        if not isinstance(obj, (InsumoTabela, ComposicaoTabela)):
            continue

        response = obj.to_pydantic()
        tabela = db.query(Tabela).filter_by(id=obj.id_tabela).first()
        classe = db.query(Classe).filter_by(id=obj.id_classe).first()
        unidade = db.query(Unidade).filter_by(id=obj.id_unidade).first()

        if not isinstance(tabela, (Tabela, type(None))):
            raise TypeError
        if not isinstance(unidade, (Unidade, type(None))):
            raise TypeError
        if not isinstance(classe, (Classe, type(None))):
            raise TypeError

        response.tabela = tabela.to_pydantic() if tabela else None
        response.unidade = unidade.to_pydantic() if unidade else None
        response.classe = classe.to_pydantic() if classe else None

        response.insumosComposicoes = []

        # breakpoint()

        if isinstance(obj, ComposicaoTabela):
            query_all = db.query(InsumoComposicao).filter_by(id_composicao=obj.id).all()
        else:
            query_all = db.query(InsumoComposicao).filter_by(id_insumo=obj.id).all()
        for ic in query_all:
            if not isinstance(ic, InsumoComposicao):
                continue
            insumo_item: Optional[InsumoItem] = (
                db.query(InsumoItem).filter_by(id=ic.id_insumo_item).first()
            )
            if insumo_item is None:
                continue
            ic_response: InsumoComposicaoResponse = ic.to_pydantic(
                insumo_item.to_pydantic()
            )
            response.insumosComposicoes.append(ic_response)

        result.append(response)
    return result


def mount_insumo_composicao_response2(db: Session, insumos_composicoes):
    result = []
    for obj in insumos_composicoes:
        response = mount_one_insumo_composicao_response(obj, db)
        result.append(response)
    return result


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
