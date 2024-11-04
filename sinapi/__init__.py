import json
import asyncio

from contextlib import suppress
from typing import Any, Dict, Optional
from sqlalchemy.exc import InvalidRequestError

from sinapi.models import InsumoComposicaoTabela


try:
    from database import Session
    from web import get_insumos_or_compositions
    from models import (
        ComposicaoTabela,
        Estado,
        Tabela,
        Unidade,
        Classe,
        InsumoTabela,
        ComposicaoItem,
    )
except:
    from sinapi.database import Session
    from sinapi.web import get_insumos_or_compositions
    from sinapi.models import (
        ComposicaoTabela,
        Estado,
        Tabela,
        Unidade,
        Classe,
        InsumoTabela,
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

    session.merge(
        InsumoComposicaoTabela(
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
    )


def inserir_composicoes_insumo(insumo_composicao_api: dict, session):

    insumo_item = insumo_composicao_api["insumoItem"]
    inserir_insumo_item(item=insumo_item, session=session)

    session.merge(
        ComposicaoItem(
            id=insumo_composicao_api["id"],
            id_insumo=insumo_composicao_api["idInsumo"],
            id_insumo_item=insumo_composicao_api["idInsumoItem"],
            valor_onerado=insumo_composicao_api["valorOnerado"],
            valor_nao_onerado=insumo_composicao_api["valorNaoOnerado"],
            coeficiente=insumo_composicao_api["coeficiente"],
            excluido=insumo_composicao_api["excluido"],
        )
    )


def inserir_composicao(i: Dict[str, Any], session):

    inserir_unidade(i["unidade"], session)
    inserir_tabela(i["tabela"], session)
    inserir_classe(i["classe"], session)
    item = ComposicaoTabela(
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


def inserir_insumo(i: Dict[str, Any], session):
    inserir_unidade(i["unidade"], session)
    inserir_tabela(i["tabela"], session)
    inserir_classe(i["classe"], session)
    item = InsumoTabela(
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


def inserir_composicoes(composicoes):
    with Session() as session:
        for composicao in composicoes:
            inserir_composicao(composicao, session)
        session.commit()


async def cadastrar_composicoes():
    async for composicao_response in get_insumos_or_compositions(ano="2024"):
        composicao_data = composicao_response.model_dump()
        inserir_composicoes(composicao_data["items"])


async def main():
    await cadastrar_composicoes()
    while True:
        print("Terminou!")
        await asyncio.sleep(3600)


# def chunk_list(lst, chunk_size):
#     """Divide uma lista em múltiplas listas de tamanho especificado."""
#     for i in range(0, len(lst), chunk_size):
#         yield lst[i : i + chunk_size]


# def get_all_ids(Table, session) -> list:
#     """Retorna uma lista de todos os IDs da tabela ExampleTable."""
#     from sqlalchemy import select

#     stmt = select(Table.id)
#     result = session.execute(stmt)
#     return [row[0] for row in result]


# async def main():
#     with Session() as session:
#         batch_size = 20_000  # Tamanho do lote

#         list_ids = get_all_ids(ComposicaoMontada, session)
#         chunks = list(chunk_list(list_ids, batch_size))

#         for chunk in chunks:
#             for id in chunk:
#                 comp: Optional[ComposicaoMontada] = (
#                     session.query(ComposicaoMontada).filter_by(id=id).first()
#                 )

#                 assert comp

#                 item = ComposicaoItem(
#                     id=comp.id,
#                     id_insumo=comp.id_insumo or comp.id_composicao,
#                     id_insumo_item=comp.id_insumo_item,
#                     valor_onerado=comp.valor_onerado,
#                     valor_nao_onerado=comp.valor_nao_onerado,
#                     coeficiente=comp.coeficiente,
#                     excluido=comp.excluido,
#                 )

#                 session.merge(item)
#                 print("-")

#             session.commit()
#             print("\n\n")
