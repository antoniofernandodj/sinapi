import json
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from models import (
    Base,
    Tabela,
    Unidade,
    Classe,
    Insumo,
    InsumoItem,
    InsumoComposicao1,
    InsumoComposicao2,
)


def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def inserir_classes(session: Session, data):
    for item in data:
        classe = session.query(Classe).filter_by(id=item["classe"]["id"]).first()
        if not classe:
            classe = Classe(
                id=item["classe"]["id"],
                nome=item["classe"]["nome"],
                excluido=item["classe"]["excluido"],
            )
            session.add(classe)
            session.commit()


def inserir_tabelas(session: Session, data):
    for item in data:
        tabela = session.query(Tabela).filter_by(id=item["tabela"]["id"]).first()
        if not tabela:
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
            session.add(tabela)
            session.commit()


def inserir_unidades(session: Session, data):
    for item in data:
        unidade = session.query(Unidade).filter_by(id=item["unidade"]["id"]).first()
        if not unidade:
            unidade = Unidade(
                id=item["unidade"]["id"],
                nome=item["unidade"]["nome"],
                excluido=item["unidade"]["excluido"],
            )
            session.add(unidade)
            session.commit()


def inserir_composicoes_insumo(session: Session, data, insumo: Insumo):
    for item in data:
        for composicao_item in item["insumosComposicoes"]:

            insumo_item = (
                session.query(InsumoItem)
                .filter_by(id=composicao_item["insumoItem"]["id"])
                .first()
            )
            if not insumo_item:
                insumo_item = InsumoItem(
                    id=composicao_item["insumoItem"]["id"],
                    nome=composicao_item["insumoItem"]["nome"],
                    codigo=composicao_item["insumoItem"]["codigo"],
                    id_tabela=composicao_item["insumoItem"]["idTabela"],
                    id_unidade=composicao_item["insumoItem"]["idUnidade"],
                    # descobrir ao que se refere
                    id_classe=composicao_item["insumoItem"]["idClasse"],
                    valor_onerado=composicao_item["insumoItem"]["valorOnerado"],
                    valor_nao_onerado=composicao_item["insumoItem"]["valorNaoOnerado"],
                    composicao=composicao_item["insumoItem"]["composicao"],
                    percentual_mao_de_obra=composicao_item["insumoItem"].get(
                        "percentualMaoDeObra"
                    ),
                    percentual_material=composicao_item["insumoItem"].get(
                        "percentualMaterial"
                    ),
                    percentual_equipamentos=composicao_item["insumoItem"].get(
                        "percentualEquipamentos"
                    ),
                    percentual_servicos_terceiros=composicao_item["insumoItem"].get(
                        "percentualServicosTerceiros"
                    ),
                    percentual_outros=composicao_item["insumoItem"].get(
                        "percentualOutros"
                    ),
                    excluido=composicao_item["insumoItem"]["excluido"],
                )

                session.add(insumo_item)
                session.commit()

                insumo_composicao = InsumoComposicao1(
                    id=composicao_item["id"],
                    id_insumo=insumo.id,
                    id_insumo_item=insumo_item.id,
                    valor_onerado=composicao_item["valorOnerado"],
                    valor_nao_onerado=composicao_item["valorNaoOnerado"],
                    coeficiente=composicao_item["coeficiente"],
                    excluido=composicao_item["excluido"],
                )
                try:
                    session.add(insumo_composicao)
                    session.commit()
                except:
                    breakpoint()

    session.commit()


def inserir_insumos(session, data):
    for item in data:
        insumo = (
            session.query(Insumo)
            .filter_by(codigo=item["codigo"], nome=item["nome"])
            .first()
        )
        if not insumo:
            insumo = Insumo(
                id=item["id"],
                nome=item["nome"],
                codigo=item["codigo"],
                id_tabela=item["tabela"]["id"],
                id_unidade=item["unidade"]["id"],
                id_classe=item["classe"]["id"],
                valor_onerado=item["valorOnerado"],
                valor_nao_onerado=item["valorNaoOnerado"],
                composicao=item["composicao"],
                percentual_mao_de_obra=item["percentualMaoDeObra"],
                percentual_material=item["percentualMaterial"],
                percentual_equipamentos=item["percentualEquipamentos"],
                percentual_servicos_terceiros=item["percentualServicosTerceiros"],
                percentual_outros=item["percentualOutros"],
                excluido=item["excluido"],
            )
            session.add(insumo)
            session.commit()
            session.refresh(insumo)
            inserir_composicoes_insumo(session, data, insumo)


def main():
    engine = create_engine("mysql+pymysql://itemize:I*2021t1201@localhost/insumos")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    data = load_json("insumos.json")

    inserir_classes(session, data)
    inserir_tabelas(session, data)
    inserir_unidades(session, data)
    inserir_insumos(session, data)


if __name__ == "__main__":
    main()
