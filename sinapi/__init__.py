import json
import asyncio

from contextlib import suppress
from typing import Any, Dict, Iterator, List, Optional, Type, Union
from sqlalchemy.exc import InvalidRequestError

from sinapi.models import InsumoComposicaoTabela


try:
    from database import Session
    from web import get_insumos_or_compositions  # type: ignore
    from models import (
        ComposicaoTabela,
        Estado,
        Tabela,
        Unidade,
        Classe,
        InsumoTabela,
        # InsumoItem,
        ComposicaoMontada,
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
        # InsumoItem,
        ComposicaoMontada,
    )


# def load_json(file_path):
#     with open(file_path, "r", encoding="utf-8") as f:
#         return json.load(f)


# def inserir_estado(data, session):

#     session.merge(
#         Estado(  # type: ignore
#             id=data["id"],  # type: ignore
#             nome=data["nome"],  # type: ignore
#             uf=data["uf"],  # type: ignore
#             ibge=data["ibge"],  # type: ignore
#             excluido=data["excluido"] if data["excluido"] is not None else False,  # type: ignore
#         )
#     )


# def inserir_unidade(item: Optional[dict], session):
#     if item is None:
#         return

#     session.merge(
#         Unidade(
#             id=item["id"],  # type: ignore
#             nome=item["nome"],  # type: ignore
#             excluido=item["excluido"],  # type: ignore
#         )
#     )


# def inserir_classe(item: Optional[dict], session):
#     if item is None:
#         return

#     session.merge(
#         Classe(
#             id=item["id"],  # type: ignore
#             nome=item["nome"],  # type: ignore
#             excluido=item["excluido"],  # type: ignore
#         )
#     )


# def inserir_tabela(item: Optional[dict], session):
#     if item is None:
#         return

#     session.merge(
#         Tabela(
#             id=item["id"],  # type: ignore
#             nome=item["nome"],  # type: ignore
#             id_estado=item["idEstado"],  # type: ignore
#             mes=item["mes"],  # type: ignore
#             ano=item["ano"],  # type: ignore
#             data_hora_atualizacao=item["dataHoraAtualizacao"],  # type: ignore
#             id_tipo_tabela=item["idTipoTabela"],  # type: ignore
#             excluido=item["excluido"],  # type: ignore
#         )
#     )


# # TODO
# def inserir_insumo_item(item: Optional[dict], session):

#     raise NotImplementedError
#     if item is None:
#         return

#     if item["unidade"]:
#         inserir_unidade(item["unidade"], session)

#     if item["tabela"]:
#         inserir_tabela(item["tabela"], session)

#     if item["composicao"]:
#         main_insert(item, ComposicaoTabela, session)

#     session.merge(
#         InsumoItem(
#             id=item["id"],  # type: ignore
#             nome=item["nome"],  # type: ignore
#             codigo=item["codigo"],  # type: ignore
#             id_tabela=item["idTabela"],  # type: ignore
#             id_unidade=item["idUnidade"],  # type: ignore
#             id_classe=item["idClasse"],  # type: ignore
#             valor_onerado=item["valorOnerado"],  # type: ignore
#             valor_nao_onerado=item["valorNaoOnerado"],  # type: ignore
#             composicao=item["composicao"],  # type: ignore
#             percentual_mao_de_obra=item.get("percentualMaoDeObra"),  # type: ignore
#             percentual_material=item.get("percentualMaterial"),  # type: ignore
#             percentual_equipamentos=item.get("percentualEquipamentos"),  # type: ignore
#             percentual_servicos_terceiros=item.get("percentualServicosTerceiros"),  # type: ignore
#             percentual_outros=item.get("percentualOutros"),  # type: ignore
#             excluido=item["excluido"],  # type: ignore
#         )
#     )


# def inserir_composicoes_insumo(
#     insumo_composicao_api: dict, insumo: Union[InsumoTabela, ComposicaoTabela], session
# ):

#     insumo_item = insumo_composicao_api["insumoItem"]

#     inserir_insumo_item(item=insumo_item, session=session)

#     if isinstance(insumo, InsumoTabela):
#         session.merge(
#             ComposicaoMontada(
#                 id=insumo_composicao_api["id"],  # type: ignore
#                 id_insumo=insumo.id,  # type: ignore
#                 id_composicao=None,  # type: ignore
#                 id_insumo_item=insumo_item["id"],  # type: ignore
#                 valor_onerado=insumo_composicao_api["valorOnerado"],  # type: ignore
#                 valor_nao_onerado=insumo_composicao_api["valorNaoOnerado"],  # type: ignore
#                 coeficiente=insumo_composicao_api["coeficiente"],  # type: ignore
#                 excluido=insumo_composicao_api["excluido"],  # type: ignore
#             )
#         )

#     elif isinstance(insumo, ComposicaoTabela):
#         session.merge(
#             ComposicaoMontada(
#                 id=insumo_composicao_api["id"],  # type: ignore
#                 id_insumo=None,  # type: ignore
#                 id_composicao=insumo.id,  # type: ignore
#                 id_insumo_item=insumo_item["id"],  # type: ignore
#                 valor_onerado=insumo_composicao_api["valorOnerado"],  # type: ignore
#                 valor_nao_onerado=insumo_composicao_api["valorNaoOnerado"],  # type: ignore
#                 coeficiente=insumo_composicao_api["coeficiente"],  # type: ignore
#                 excluido=insumo_composicao_api["excluido"],  # type: ignore
#             )
#         )


# # TODO
# def vincular_item_de_composicao_a_uma_composicao(
#     insumo_composicao_api: dict, insumo: Union[InsumoTabela, ComposicaoTabela], session
# ):
#     raise NotImplementedError


# def inserir_composicao(i: Dict[str, Any], session):
#     inserir_unidade(i["unidade"], session)
#     inserir_tabela(i["tabela"], session)
#     inserir_classe(i["classe"], session)
#     item = ComposicaoTabela(
#         id=i["id"],  # type: ignore
#         nome=i["nome"],  # type: ignore
#         codigo=i["codigo"],  # type: ignore
#         id_tabela=i["tabela"]["id"],  # type: ignore
#         id_unidade=i["unidade"]["id"],  # type: ignore
#         id_classe=i["classe"]["id"],  # type: ignore
#         valor_onerado=i["valorOnerado"],  # type: ignore
#         valor_nao_onerado=i["valorNaoOnerado"],  # type: ignore
#         composicao=i["composicao"],  # type: ignore
#         percentual_mao_de_obra=i["percentualMaoDeObra"],  # type: ignore
#         percentual_material=i["percentualMaterial"],  # type: ignore
#         percentual_equipamentos=i["percentualEquipamentos"],  # type: ignore
#         percentual_servicos_terceiros=i["percentualServicosTerceiros"],  # type: ignore
#         percentual_outros=i["percentualOutros"],  # type: ignore
#         excluido=i["excluido"],  # type: ignore
#     )
#     session.merge(item)
#     session.flush()
#     with suppress(InvalidRequestError):
#         session.refresh(item)

#     for insumo_composicao in i["insumosComposicoes"]:
#         inserir_composicoes_insumo(insumo_composicao, item, session)


# def inserir_insumo(i: Dict[str, Any], session):
#     inserir_unidade(i["unidade"], session)
#     inserir_tabela(i["tabela"], session)
#     inserir_classe(i["classe"], session)
#     item = InsumoTabela(
#         id=i["id"],  # type: ignore
#         nome=i["nome"],  # type: ignore
#         codigo=i["codigo"],  # type: ignore
#         id_tabela=i["tabela"]["id"],  # type: ignore
#         id_unidade=i["unidade"]["id"],  # type: ignore
#         id_classe=i["classe"]["id"],  # type: ignore
#         valor_onerado=i["valorOnerado"],  # type: ignore
#         valor_nao_onerado=i["valorNaoOnerado"],  # type: ignore
#         composicao=i["composicao"],  # type: ignore
#         percentual_mao_de_obra=i["percentualMaoDeObra"],  # type: ignore
#         percentual_material=i["percentualMaterial"],  # type: ignore
#         percentual_equipamentos=i["percentualEquipamentos"],  # type: ignore
#         percentual_servicos_terceiros=i["percentualServicosTerceiros"],  # type: ignore
#         percentual_outros=i["percentualOutros"],  # type: ignore
#         excluido=i["excluido"],  # type: ignore
#     )
#     session.merge(item)
#     session.flush()
#     with suppress(InvalidRequestError):
#         session.refresh(item)


# def inserir_insumos(insumos, estado_data):
#     with Session() as session:
#         inserir_estado(estado_data, session)
#         for insumo in insumos:
#             inserir_insumo(insumo, session)
#         session.commit()


# def inserir_composicoes(composicoes, estado_data):
#     with Session() as session:
#         inserir_estado(estado_data, session)
#         for composicao in composicoes:
#             inserir_composicao(composicao, session)
#         session.commit()


# async def cadastrar_insumos():
#     async for insumo_response, estado_response in get_insumos_or_compositions(
#         composicao=False, ano="2024"
#     ):

#         insumo_data = insumo_response.model_dump()  # type: ignore
#         estado_data = estado_response.model_dump()  # type: ignore
#         inserir_insumos(insumo_data["items"], estado_data)


# async def cadastrar_composicoes():
#     async for composicao_response, estado_response in get_insumos_or_compositions(
#         composicao=True, ano="2024"
#     ):

#         composicao_data = composicao_response.model_dump()  # type: ignore
#         estado_data = estado_response.model_dump()  # type: ignore

#         inserir_composicoes(composicao_data["items"], estado_data)


# async def main():
#     await asyncio.gather(cadastrar_insumos(), cadastrar_composicoes())
#     while True:
#         print("Terminou!")
#         await asyncio.sleep(3600)


async def main():
    YIELD_COUNT = 10
    BATCH_SIZE = (
        100  # Limite a quantidade de objetos na memória antes de fazer um commit
    )

    with Session() as session:
        print(f"i: {session.query(InsumoTabela).count()}")
        print(f"c: {session.query(ComposicaoTabela).count()}")

        # Processar Insumos
        insumo_items = []
        insumos_iter = session.query(InsumoTabela).yield_per(YIELD_COUNT)
        for insumo in insumos_iter:
            item = InsumoComposicaoTabela(
                id=insumo.id,
                nome=insumo.nome,
                codigo=insumo.codigo,
                id_tabela=insumo.id_tabela,
                id_unidade=insumo.id_unidade,
                id_classe=insumo.id_classe,
                valor_onerado=insumo.valor_onerado,
                valor_nao_onerado=insumo.valor_nao_onerado,
                composicao=insumo.composicao,
                percentual_mao_de_obra=insumo.percentual_mao_de_obra,
                percentual_material=insumo.percentual_material,
                percentual_equipamentos=insumo.percentual_equipamentos,
                percentual_servicos_terceiros=insumo.percentual_servicos_terceiros,
                percentual_outros=insumo.percentual_outros,
                excluido=insumo.excluido,
            )
            insumo_items.append(item)

            # Commit em batches
            if len(insumo_items) >= BATCH_SIZE:
                session.bulk_save_objects(insumo_items)
                session.commit()
                insumo_items.clear()  # Limpa a lista após o commit

        # Commit qualquer restante
        if insumo_items:
            session.bulk_save_objects(insumo_items)
            session.commit()
            insumo_items.clear()

        print("Processed insumos!")

        # Processar Composições
        composicao_items = []
        composicoes_iter = session.query(ComposicaoTabela).yield_per(YIELD_COUNT)
        for composicao in composicoes_iter:
            item = InsumoComposicaoTabela(
                id=composicao.id,
                nome=composicao.nome,
                codigo=composicao.codigo,
                id_tabela=composicao.id_tabela,
                id_unidade=composicao.id_unidade,
                id_classe=composicao.id_classe,
                valor_onerado=composicao.valor_onerado,
                valor_nao_onerado=composicao.valor_nao_onerado,
                composicao=composicao.composicao,
                percentual_mao_de_obra=composicao.percentual_mao_de_obra,
                percentual_material=composicao.percentual_material,
                percentual_equipamentos=composicao.percentual_equipamentos,
                percentual_servicos_terceiros=composicao.percentual_servicos_terceiros,
                percentual_outros=composicao.percentual_outros,
                excluido=composicao.excluido,
            )
            composicao_items.append(item)

            # Commit em batches
            if len(composicao_items) >= BATCH_SIZE:
                session.bulk_save_objects(composicao_items)
                session.commit()
                composicao_items.clear()  # Limpa a lista após o commit

        # Commit qualquer restante
        if composicao_items:
            session.bulk_save_objects(composicao_items)
            session.commit()
            composicao_items.clear()

        print("Processed composicoes!")
    print("Finalizado!")
