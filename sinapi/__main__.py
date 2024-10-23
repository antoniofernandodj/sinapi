from contextlib import suppress
import json
from typing import Any, Dict, List, Optional, Type, Union
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import InvalidRequestError
import asyncio
from web import get_insumos_or_compositions
from models import (
    Base,
    ComposicaoTabela,
    Estado,
    Tabela,
    Unidade,
    Classe,
    InsumoTabela,
    InsumoItem,
    InsumoComposicao,
)

SGBD_URL = "mysql+pymysql://itemize:I*2021t1201@localhost"
DATABASE_INSUMOS_URL = "mysql+pymysql://itemize:I*2021t1201@localhost/sinapi"

with create_engine(SGBD_URL, echo=True).connect() as connection:
    connection.execute(text("CREATE DATABASE IF NOT EXISTS sinapi"))

engine = create_engine(DATABASE_INSUMOS_URL, echo=True)
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
    

def inserir_estado(data, session):
    estado = Estado(
        id=data['id'],
        nome=data['nome'],
        uf=data['uf'],
        ibge=data['ibge'],
        excluido=data['excluido'] if data['excluido'] is not None else False
    )

    session.merge(estado)
    


def inserir_tabelas(data, session):
    for item in data:
        tabela = Tabela(
            id=item["tabela"]["id"],
            nome=item["tabela"]["nome"],
            id_estado=item["tabela"]["idEstado"],
            mes=item["tabela"]["mes"],
            ano=item["tabela"]["ano"],
            data_hora_atualizacao=item["tabela"]["dataHoraAtualizacao"],
            id_tipo_tabela=item["tabela"]["idTipoTabela"],
            excluido=item["tabela"]["excluido"],
        )
        session.merge(tabela)


def inserir_unidade(item: Optional[dict], session):
    if item is None:
        return

    unidade = Unidade(
        id=item["id"],
        nome=item["nome"],
        excluido=item["excluido"],
    )
    session.merge(unidade)


def inserir_classe(item: Optional[dict], session):
    if item is None:
        return

    classe = Classe(
        id=item["id"],
        nome=item["nome"],
        excluido=item["excluido"],
    )
    session.merge(classe)


def inserir_tabela(item: Optional[dict], session):
    if item is None:
        return

    tabela = Tabela(
        id=item["id"],
        nome=item["nome"],
        id_estado=item["idEstado"],
        mes=item["mes"],
        ano=item["ano"],
        data_hora_atualizacao=item["dataHoraAtualizacao"],
        id_tipo_tabela=item["idTipoTabela"],
        excluido=item["excluido"],
    )
    session.merge(tabela)


def inserir_classes(data, session):
    for item in data:
        classe = Classe(
            id=item["classe"]["id"],
            nome=item["classe"]["nome"],
            excluido=item["classe"]["excluido"],
        )
        session.merge(classe)

def inserir_unidades(data, session):
    for item in data:
        unidade = Unidade(
            id=item["unidade"]["id"],
            nome=item["unidade"]["nome"],
            excluido=item["unidade"]["excluido"],
        )
        session.merge(unidade)

def inserir_insumo_item(item: Optional[dict], composicao_item, insumo: Union[InsumoTabela, ComposicaoTabela], session):
    if item is None:
        return

    inserir_unidade(item["unidade"], session)
    inserir_tabela(item['tabela'], session)
    insumo_item = InsumoItem(
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
    session.merge(insumo_item)

    if isinstance(insumo, InsumoTabela):
        insumo_composicao = InsumoComposicao(
            id=composicao_item["id"],
            id_insumo=insumo.id,
            id_composicao=None,
            id_insumo_item=insumo_item.id,
            valor_onerado=composicao_item["valorOnerado"],
            valor_nao_onerado=composicao_item["valorNaoOnerado"],
            coeficiente=composicao_item["coeficiente"],
            excluido=composicao_item["excluido"],
        )
    elif isinstance(insumo, ComposicaoTabela):
        insumo_composicao = InsumoComposicao(
            id=composicao_item["id"],
            id_insumo=None,
            id_composicao=insumo.id,
            id_insumo_item=insumo_item.id,
            valor_onerado=composicao_item["valorOnerado"],
            valor_nao_onerado=composicao_item["valorNaoOnerado"],
            coeficiente=composicao_item["coeficiente"],
            excluido=composicao_item["excluido"],
        )
    
    session.merge(insumo_composicao)

def inserir_composicoes_insumo(data, insumo: Union[InsumoTabela, ComposicaoTabela], session):
    for i in data:
        inserir_insumo_item(i["insumoItem"], i, insumo, session)

def main_insert(i: Dict[str, Any], Model: Union[Type[InsumoTabela], Type[ComposicaoTabela]], session):
    inserir_unidade(i["unidade"], session)
    inserir_tabela(i["tabela"], session)
    inserir_classe(i["classe"], session)
    item = Model(
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

    inserir_composicoes_insumo(i['insumosComposicoes'], item, session)

def inserir_insumos(data, estado_data):
    with Session() as session:
        inserir_estado(estado_data, session)
        for i in data:
            main_insert(i, InsumoTabela, session)
        session.commit()

def inserir_composicoes(data, estado_data):
    with Session() as session:
        inserir_estado(estado_data, session)
        for i in data:
            main_insert(i, ComposicaoTabela, session)
        session.commit()

async def cadastrar_insumos():
    async for insumo_response, estado_response in get_insumos_or_compositions(
        composicao=False,
        ano='2024'
    ):
        insumo_data = insumo_response.model_dump()
        estado_data = estado_response.model_dump()
        print(f'Got insumo!: {insumo_response.model_json_schema()}')
        inserir_insumos(insumo_data['items'], estado_data)

async def cadastrar_composicoes():
    async for composicao_response, estado_response in get_insumos_or_compositions(
        composicao=True,
        ano='2024'
    ):
        composicao_data = composicao_response.model_dump()
        estado_data = estado_response.model_dump()

        print(f'Got composicao!: {composicao_response.model_json_schema()}')
        inserir_composicoes(composicao_data['items'], estado_data)

async def main():
    await asyncio.gather(cadastrar_insumos(), cadastrar_composicoes())
    while True:
        print('Terminou!')
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
