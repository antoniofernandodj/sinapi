from contextlib import suppress
import json
from typing import Any, Dict, Optional, Type, Union
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import InvalidRequestError
import asyncio
from web import get_insumos_or_compositions

try:
    from models import (
        Base,
        ComposicaoTabela,
        Tabela,
        Unidade,
        Classe,
        InsumoTabela,
        InsumoItem,
        InsumoComposicao,
    )
except:
    from sinapi.models import (
        Base,
        ComposicaoTabela,
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

engine = create_engine(DATABASE_INSUMOS_URL, echo=False)
Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(engine)


def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
    
def inserir_tabelas(data):
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
    session.commit()

def inserir_classes(data):
    for item in data:
        classe = Classe(
            id=item["classe"]["id"],
            nome=item["classe"]["nome"],
            excluido=item["classe"]["excluido"],
        )
        session.merge(classe)
    session.commit()

def inserir_unidades(data):
    for item in data:
        unidade = Unidade(
            id=item["unidade"]["id"],
            nome=item["unidade"]["nome"],
            excluido=item["unidade"]["excluido"],
        )
        session.merge(unidade)
    session.commit()

def inserir_unidade(item: Optional[dict]):
    if item is None:
        return

    unidade = Unidade(
        id=item["id"],
        nome=item["nome"],
        excluido=item["excluido"],
    )
    session.merge(unidade)
    session.commit()

def inserir_classe(item: Optional[dict]):
    if item is None:
        return

    classe = Classe(
        id=item["id"],
        nome=item["nome"],
        excluido=item["excluido"],
    )
    session.merge(classe)
    session.commit()

def inserir_tabela(item: Optional[dict]):
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
    session.commit()

def inserir_insumo_item(
    item: Optional[dict],
    composicao_item,
    insumo: Union[InsumoTabela, ComposicaoTabela],
):
    if item is None:
        return

    inserir_unidade(item["unidade"])
    inserir_tabela(item['tabela'])
    insumo_item = InsumoItem(
        id=item["id"],
        nome=item["nome"],
        codigo=item["codigo"],
        id_tabela=item["idTabela"],
        id_unidade=item["idUnidade"],
        # descobrir ao que se refere
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
    session.commit()

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
    session.commit()

def inserir_composicoes_insumo(data, insumo: Union[InsumoTabela, ComposicaoTabela]):
    for i in data:
        inserir_insumo_item(i["insumoItem"], i, insumo)

def main_insert(
    i: Dict[str, Any],
    Model: Union[Type[InsumoTabela], Type[ComposicaoTabela]]
):

    inserir_unidade(i["unidade"])
    inserir_tabela(i["tabela"])
    inserir_classe(i["classe"])
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
    session.commit()
    session.flush()
    with suppress(InvalidRequestError):
        session.refresh(item)
    inserir_composicoes_insumo(i['insumosComposicoes'], item)

def inserir_insumos(data):
    for i in data:
        main_insert(i, InsumoTabela)

def inserir_composicoes(data):
    for i in data:
        main_insert(i, ComposicaoTabela)

def insert_composicoes(composicao: Dict[str, Any]):

    inserir_classes(composicao)
    inserir_tabelas(composicao)
    inserir_unidades(composicao)
    inserir_composicoes(composicao)

def insert_insumos(insumo: Dict[str, Any]):

    inserir_classes(insumo)
    inserir_tabelas(insumo)
    inserir_unidades(insumo)
    inserir_insumos(insumo)


async def cadastrar_insumos():
    async for insumo_response, estado_response in get_insumos_or_compositions(
        composicao=False,
        ano='2024'
    ):
        insumo_data = insumo_response.model_dump()
        estado_data = estado_response.model_dump()
        print(f'Got insumo!: {insumo_response.model_json_schema()}')
        insert_insumos(insumo_data['items'])
        

async def cadastrar_composicoes():
    async for composicao_response, estado_response in get_insumos_or_compositions(
        composicao=True,
        ano='2024'
    ):
        composicao_data = composicao_response.model_dump()
        estado_data = estado_response.model_dump()
        print(f'Got composicao!: {composicao_response.model_json_schema()}')
        insert_composicoes(composicao_data['items'])


async def main():
    await asyncio.gather(cadastrar_insumos(), cadastrar_composicoes())


if __name__ == "__main__":
    asyncio.run(main())