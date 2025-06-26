import asyncio
from contextlib import suppress
from typing import Any, Dict, Optional
from sqlalchemy.exc import InvalidRequestError, IntegrityError

try:
    from database import SessionLocal
    from web import get_insumos_or_compositions
    from models import (
        Estado,
        Tabela,
        Unidade,
        Classe,
        ComposicaoItem,
        InsumoComposicaoTabela
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
        InsumoComposicaoTabela
    )

# Função auxiliar para inserir com verificação
def safe_merge(session, entity, data, model_class, id_field='id'):
    """Insere ou atualiza uma entidade com verificação de existência"""
    existing = session.get(model_class, data[id_field])
    if existing:
        for key, value in data.items():
            setattr(existing, key, value)
    else:
        session.add(model_class(**data))
    session.flush()

def inserir_estado(data, session):
    safe_merge(session, data, Estado, {
        'id': data['id'],
        'nome': data['nome'],
        'uf': data['uf'],
        'ibge': data['ibge'],
        'excluido': data.get('excluido', False)
    })

def inserir_unidade(item: Optional[dict], session):
    if not item:
        return
    safe_merge(session, item, Unidade, {
        'id': item['id'],
        'nome': item['nome'],
        'excluido': item.get('excluido')
    })

def inserir_classe(item: Optional[dict], session):
    if not item:
        return
    safe_merge(session, item, Classe, {
        'id': item['id'],
        'nome': item['nome'],
        'excluido': item.get('excluido')
    })

def inserir_tabela(item: Optional[dict], session):
    if not item:
        return
    safe_merge(session, item, Tabela, {
        'id': item['id'],
        'nome': item['nome'],
        'id_estado': item['idEstado'],
        'mes': item['mes'],
        'ano': item['ano'],
        'data_hora_atualizacao': item['dataHoraAtualizacao'],
        'id_tipo_tabela': item['idTipoTabela'],
        'excluido': item.get('excluido')
    })

def inserir_insumo_item(item: dict, session):
    # Persistir dependências primeiro
    if item.get('unidade'):
        inserir_unidade(item['unidade'], session)
    if item.get('tabela'):
        inserir_tabela(item['tabela'], session)
    if item.get('classe'):
        inserir_classe(item['classe'], session)

    # Certificar que a classe existe
    if 'idClasse' in item and not session.get(Classe, item['idClasse']):
        raise ValueError(f"Classe {item['idClasse']} não encontrada para insumo {item['id']}")

    # Preparar dados do insumo
    insumo_data = {
        'id': item['id'],
        'nome': item['nome'],
        'codigo': item['codigo'],
        'id_tabela': item['idTabela'],
        'id_unidade': item['idUnidade'],
        'id_classe': item['idClasse'],
        'valor_onerado': item['valorOnerado'],
        'valor_nao_onerado': item['valorNaoOnerado'],
        'composicao': item['composicao'],
        'percentual_mao_de_obra': item.get('percentualMaoDeObra'),
        'percentual_material': item.get('percentualMaterial'),
        'percentual_equipamentos': item.get('percentualEquipamentos'),
        'percentual_servicos_terceiros': item.get('percentualServicosTerceiros'),
        'percentual_outros': item.get('percentualOutros'),
        'excluido': item.get('excluido')
    }

    safe_merge(session, insumo_data, InsumoComposicaoTabela)

def inserir_composicoes_insumo(insumo_composicao_api: dict, session):
    if not insumo_composicao_api.get('insumoItem'):
        return

    inserir_insumo_item(insumo_composicao_api['insumoItem'], session)

    composicao_data = {
        'id': insumo_composicao_api['id'],
        'id_insumo': insumo_composicao_api['idInsumo'],
        'id_insumo_item': insumo_composicao_api['idInsumoItem'],
        'valor_onerado': insumo_composicao_api['valorOnerado'],
        'valor_nao_onerado': insumo_composicao_api['valorNaoOnerado'],
        'coeficiente': insumo_composicao_api['coeficiente'],
        'excluido': insumo_composicao_api.get('excluido')
    }

    safe_merge(session, composicao_data, ComposicaoItem)

def inserir_composicao(i: Dict[str, Any], session):
    try:
        # Persistir dependências primeiro com flush explícito
        if i.get('unidade'):
            inserir_unidade(i['unidade'], session)
            session.flush()

        if i.get('tabela'):
            inserir_tabela(i['tabela'], session)
            session.flush()

        if i.get('classe'):
            inserir_classe(i['classe'], session)
            session.flush()

        # Verificar se todas as dependências foram persistidas
        required_deps = {
            'id_tabela': i['tabela']['id'] if i.get('tabela') else None,
            'id_unidade': i['unidade']['id'] if i.get('unidade') else None,
            'id_classe': i['classe']['id'] if i.get('classe') else None
        }

        for field, value in required_deps.items():
            if value is None:
                raise ValueError(f"Valor faltando para {field} na composição {i['id']}")

            # Verificar se a dependência existe no banco
            model_map = {
                'id_tabela': Tabela,
                'id_unidade': Unidade,
                'id_classe': Classe
            }

            if not session.get(model_map[field], value):
                raise ValueError(f"{field} {value} não encontrado para composição {i['id']}")

        # Preparar dados da composição principal
        composicao_data = {
            'id': i['id'],
            'nome': i['nome'],
            'codigo': i['codigo'],
            'id_tabela': required_deps['id_tabela'],
            'id_unidade': required_deps['id_unidade'],
            'id_classe': required_deps['id_classe'],
            'valor_onerado': i['valorOnerado'],
            'valor_nao_onerado': i['valorNaoOnerado'],
            'composicao': i['composicao'],
            'percentual_mao_de_obra': i.get('percentualMaoDeObra'),
            'percentual_material': i.get('percentualMaterial'),
            'percentual_equipamentos': i.get('percentualEquipamentos'),
            'percentual_servicos_terceiros': i.get('percentualServicosTerceiros'),
            'percentual_outros': i.get('percentualOutros'),
            'excluido': i.get('excluido')
        }

        safe_merge(session, composicao_data, InsumoComposicaoTabela)
        session.flush()

        # Processar itens da composição
        for insumo_composicao in i.get('insumosComposicoes', []):
            inserir_composicoes_insumo(insumo_composicao, session)

        return True

    except Exception as e:
        session.rollback()
        print(f"Erro ao processar composição {i.get('id')}: {str(e)}")
        return False

async def cadastrar_composicoes():
    with SessionLocal() as session:
        async for item in get_insumos_or_compositions():
            composicao_data = item.model_dump()
            try:
                success = inserir_composicao(composicao_data, session)
                if success:
                    session.commit()
                    print(f"Composição {composicao_data['id']} inserida com sucesso")
                else:
                    print(f"Falha ao inserir composição {composicao_data['id']}")
            except Exception as e:
                session.rollback()
                print(f"Erro crítico ao inserir composição {composicao_data.get('id')}: {str(e)}")

        print("Processamento concluído")

async def main():
    await cadastrar_composicoes()
    while True:
        print("Aguardando próxima execução...")
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
