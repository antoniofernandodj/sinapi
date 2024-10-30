import json
import asyncio

from contextlib import suppress
from typing import Any, Dict, Optional, Type, Union
from sqlalchemy.exc import InvalidRequestError


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
        InsumoItem,
        InsumoComposicao,
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
        InsumoItem,
        InsumoComposicao,
    )


def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def inserir_estado(data, session):

    session.merge(
        Estado(  # type: ignore
            id=data["id"],  # type: ignore
            nome=data["nome"],  # type: ignore
            uf=data["uf"],  # type: ignore
            ibge=data["ibge"],  # type: ignore
            excluido=data["excluido"] if data["excluido"] is not None else False,  # type: ignore
        )
    )


def inserir_unidade(item: Optional[dict], session):
    if item is None:
        return

    session.merge(
        Unidade(
            id=item["id"],  # type: ignore
            nome=item["nome"],  # type: ignore
            excluido=item["excluido"],  # type: ignore
        )
    )


def inserir_classe(item: Optional[dict], session):
    if item is None:
        return

    session.merge(
        Classe(
            id=item["id"],  # type: ignore
            nome=item["nome"],  # type: ignore
            excluido=item["excluido"],  # type: ignore
        )
    )


def inserir_tabela(item: Optional[dict], session):
    if item is None:
        return

    session.merge(
        Tabela(
            id=item["id"],  # type: ignore
            nome=item["nome"],  # type: ignore
            id_estado=item["idEstado"],  # type: ignore
            mes=item["mes"],  # type: ignore
            ano=item["ano"],  # type: ignore
            data_hora_atualizacao=item["dataHoraAtualizacao"],  # type: ignore
            id_tipo_tabela=item["idTipoTabela"],  # type: ignore
            excluido=item["excluido"],  # type: ignore
        )
    )


def inserir_insumo_item(item: Optional[dict], session):
    if item is None:
        return

    if item["unidade"]:
        inserir_unidade(item["unidade"], session)

    if item["tabela"]:
        inserir_tabela(item["tabela"], session)

    session.merge(
        InsumoItem(
            id=item["id"],  # type: ignore
            nome=item["nome"],  # type: ignore
            codigo=item["codigo"],  # type: ignore
            id_tabela=item["idTabela"],  # type: ignore
            id_unidade=item["idUnidade"],  # type: ignore
            id_classe=item["idClasse"],  # type: ignore
            valor_onerado=item["valorOnerado"],  # type: ignore
            valor_nao_onerado=item["valorNaoOnerado"],  # type: ignore
            composicao=item["composicao"],  # type: ignore
            percentual_mao_de_obra=item.get("percentualMaoDeObra"),  # type: ignore
            percentual_material=item.get("percentualMaterial"),  # type: ignore
            percentual_equipamentos=item.get("percentualEquipamentos"),  # type: ignore
            percentual_servicos_terceiros=item.get("percentualServicosTerceiros"),  # type: ignore
            percentual_outros=item.get("percentualOutros"),  # type: ignore
            excluido=item["excluido"],  # type: ignore
        )
    )


def inserir_composicoes_insumo(
    insumo_composicao_api: dict, insumo: Union[InsumoTabela, ComposicaoTabela], session
):

    insumo_item = insumo_composicao_api["insumoItem"]

    inserir_insumo_item(item=insumo_item, session=session)

    if isinstance(insumo, InsumoTabela):
        session.merge(
            InsumoComposicao(
                id=insumo_composicao_api["id"],  # type: ignore
                id_insumo=insumo.id,  # type: ignore
                id_composicao=None,  # type: ignore
                id_insumo_item=insumo_item["id"],  # type: ignore
                valor_onerado=insumo_composicao_api["valorOnerado"],  # type: ignore
                valor_nao_onerado=insumo_composicao_api["valorNaoOnerado"],  # type: ignore
                coeficiente=insumo_composicao_api["coeficiente"],  # type: ignore
                excluido=insumo_composicao_api["excluido"],  # type: ignore
            )
        )

    elif isinstance(insumo, ComposicaoTabela):
        session.merge(
            InsumoComposicao(
                id=insumo_composicao_api["id"],  # type: ignore
                id_insumo=None,  # type: ignore
                id_composicao=insumo.id,  # type: ignore
                id_insumo_item=insumo_item["id"],  # type: ignore
                valor_onerado=insumo_composicao_api["valorOnerado"],  # type: ignore
                valor_nao_onerado=insumo_composicao_api["valorNaoOnerado"],  # type: ignore
                coeficiente=insumo_composicao_api["coeficiente"],  # type: ignore
                excluido=insumo_composicao_api["excluido"],  # type: ignore
            )
        )


def main_insert(
    i: Dict[str, Any], Model: Union[Type[InsumoTabela], Type[ComposicaoTabela]], session
):
    inserir_unidade(i["unidade"], session)
    inserir_tabela(i["tabela"], session)
    inserir_classe(i["classe"], session)
    item = Model(
        id=i["id"],  # type: ignore
        nome=i["nome"],  # type: ignore
        codigo=i["codigo"],  # type: ignore
        id_tabela=i["tabela"]["id"],  # type: ignore
        id_unidade=i["unidade"]["id"],  # type: ignore
        id_classe=i["classe"]["id"],  # type: ignore
        valor_onerado=i["valorOnerado"],  # type: ignore
        valor_nao_onerado=i["valorNaoOnerado"],  # type: ignore
        composicao=i["composicao"],  # type: ignore
        percentual_mao_de_obra=i["percentualMaoDeObra"],  # type: ignore
        percentual_material=i["percentualMaterial"],  # type: ignore
        percentual_equipamentos=i["percentualEquipamentos"],  # type: ignore
        percentual_servicos_terceiros=i["percentualServicosTerceiros"],  # type: ignore
        percentual_outros=i["percentualOutros"],  # type: ignore
        excluido=i["excluido"],  # type: ignore
    )
    session.merge(item)
    session.flush()
    with suppress(InvalidRequestError):
        session.refresh(item)

    for insumo_composicao in i["insumosComposicoes"]:
        inserir_composicoes_insumo(insumo_composicao, item, session)


def inserir_insumos(data, estado_data):
    with Session() as session:
        inserir_estado(estado_data, session)
        for i in data:
            main_insert(i, InsumoTabela, session)
        session.commit()


def inserir_composicoes(data, estado_data):
    with Session() as session:

        session.autoflush = False

        inserir_estado(estado_data, session)
        for i in data:
            main_insert(i, ComposicaoTabela, session)
        session.commit()


async def cadastrar_insumos():
    async for insumo_response, estado_response in get_insumos_or_compositions(
        composicao=False, ano="2024"
    ):

        insumo_data = insumo_response.model_dump()  # type: ignore
        estado_data = estado_response.model_dump()  # type: ignore
        inserir_insumos(insumo_data["items"], estado_data)


async def cadastrar_composicoes():
    async for composicao_response, estado_response in get_insumos_or_compositions(
        composicao=True, ano="2024"
    ):

        composicao_data = composicao_response.model_dump()  # type: ignore
        estado_data = estado_response.model_dump()  # type: ignore

        inserir_composicoes(composicao_data["items"], estado_data)


async def main():
    await asyncio.gather(cadastrar_insumos(), cadastrar_composicoes())
    while True:
        print("Terminou!")
        await asyncio.sleep(3600)
