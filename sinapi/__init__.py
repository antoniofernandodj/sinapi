import asyncio

from contextlib import suppress
from typing import Any, Dict, Optional
from sqlalchemy.exc import InvalidRequestError

from sinapi.models import InsumoComposicaoTabela


try:
    from database import SessionLocal
    from web import get_insumos_or_compositions
    from models import (
        Estado,
        Tabela,
        Unidade,
        Classe,
        ComposicaoItem,
    )
except:
    from sinapi.database import SessionLocal
    from sinapi.web import get_insumos_or_compositions
    from sinapi.models import (
        Estado,
        Tabela,
        Unidade,
        Classe,
        ComposicaoItem,
    )


def inserir_estado(data, session):

    session.merge(
        Estado(
            id=data["id"],
            nome=data["nome"],
            uf=data["uf"],
            ibge=data["ibge"],
            excluido=data["excluido"] if data["excluido"] is not None else False,
        )
    )


def inserir_unidade(item: Optional[dict], session):
    if item is None:
        return

    session.merge(
        Unidade(
            id=item["id"],
            nome=item["nome"],
            excluido=item["excluido"],
        )
    )


def inserir_classe(item: Optional[dict], session):
    if item is None:
        return

    session.merge(
        Classe(
            id=item["id"],
            nome=item["nome"],
            excluido=item["excluido"],
        )
    )


def inserir_tabela(item: Optional[dict], session):
    if item is None:
        return

    session.merge(
        Tabela(
            id=item["id"],
            nome=item["nome"],
            id_estado=item["idEstado"],
            mes=item["mes"],
            ano=item["ano"],
            data_hora_atualizacao=item["dataHoraAtualizacao"],
            id_tipo_tabela=item["idTipoTabela"],
            excluido=item["excluido"],
        )
    )


def inserir_insumo_item(item: dict, session):

    if item["unidade"]:
        inserir_unidade(item["unidade"], session)
    if item["tabela"]:
        inserir_tabela(item["tabela"], session)
    if item["classe"]:
        inserir_classe(item["classe"], session)

    insumo_composicao = InsumoComposicaoTabela(
        id=item["id"],
        nome=item["nome"],
        codigo=item["codigo"],
        id_tabela=item["idTabela"],
        id_unidade=item["idUnidade"],
        id_classe=item["idClasse"],
        valor_onerado=item["valorOnerado"],
        valor_nao_onerado=item["valorNaoOnerado"],
        composicao=item["composicao"],
        percentual_mao_de_obra=item.get("percentualMaoDeObra"),
        percentual_material=item.get("percentualMaterial"),
        percentual_equipamentos=item.get("percentualEquipamentos"),
        percentual_servicos_terceiros=item.get("percentualServicosTerceiros"),
        percentual_outros=item.get("percentualOutros"),
        excluido=item["excluido"],
    )

    session.merge(insumo_composicao)
    session.flush()
    session.commit()


def inserir_composicoes_insumo(insumo_composicao_api: dict, session):

    insumo_item = insumo_composicao_api["insumoItem"]

    # with session.no_autoflush:
    #     inserir_insumo_item(insumo_item, session)

    inserir_insumo_item(item=insumo_item, session=session)

    composicao_item = ComposicaoItem(
        id=insumo_composicao_api["id"],
        id_insumo=insumo_composicao_api["idInsumo"],
        id_insumo_item=insumo_composicao_api["idInsumoItem"],
        valor_onerado=insumo_composicao_api["valorOnerado"],
        valor_nao_onerado=insumo_composicao_api["valorNaoOnerado"],
        coeficiente=insumo_composicao_api["coeficiente"],
        excluido=insumo_composicao_api["excluido"],
    )

    session.merge(composicao_item)


def inserir_composicao(i: Dict[str, Any], session):

    inserir_unidade(i["unidade"], session)
    inserir_tabela(i["tabela"], session)
    inserir_classe(i["classe"], session)
    item = InsumoComposicaoTabela(
        id=i["id"],
        nome=i["nome"],
        codigo=i["codigo"],
        id_tabela=i["tabela"]["id"],
        id_unidade=i["unidade"]["id"],
        id_classe=i["classe"]["id"],
        valor_onerado=i["valorOnerado"],
        valor_nao_onerado=i["valorNaoOnerado"],
        composicao=i["composicao"],
        percentual_mao_de_obra=i["percentualMaoDeObra"],
        percentual_material=i["percentualMaterial"],
        percentual_equipamentos=i["percentualEquipamentos"],
        percentual_servicos_terceiros=i["percentualServicosTerceiros"],
        percentual_outros=i["percentualOutros"],
        excluido=i["excluido"],
    )
    session.merge(item)
    session.flush()
    with suppress(InvalidRequestError):
        session.refresh(item)

    for insumo_composicao in i["insumosComposicoes"]:
        inserir_composicoes_insumo(insumo_composicao, session)


def inserir_composicoes(composicoes):
    with SessionLocal() as session:
        for composicao in composicoes:
            print({'composicao_id': composicao['id']})
            inserir_composicao(composicao, session)
    session.commit()


async def cadastrar_composicoes():
    with SessionLocal() as session:
        async for item in get_insumos_or_compositions():
            # composicao_data = composicao_response.model_dump()
            print(f"Cadastrando item {item.id}")
            inserir_composicao(item.model_dump(), session)
        session.commit()

        # inserir_composicoes(composicao_data["items"])


async def main():
    await cadastrar_composicoes()
    while True:
        print("Terminou!")
        await asyncio.sleep(3600)
