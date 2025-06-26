import asyncio
from contextlib import suppress
from typing import Any, Dict, Optional
from sqlalchemy.exc import InvalidRequestError, IntegrityError
import json

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

class Processor:
    def __init__(self, session):
        self.session = session

    # Função auxiliar para inserir com verificação
    def safe_merge(self, model_class, data):
        """Insere ou atualiza uma entidade com verificação de existência"""
        # Obtém o valor do campo id
        entity_id = data.get('id')
        if entity_id is None:
            raise ValueError("Campo 'id' não encontrado nos dados")

        # Tenta obter a entidade existente
        existing = self.session.get(model_class, entity_id)
        if existing:
            # Atualiza os atributos
            for key, value in data.items():
                setattr(existing, key, value)
        else:
            # Cria uma nova instância
            self.session.add(model_class(**data))
        # Força a persistência
        self.session.flush()

    def inserir_estado(self, data):
        self.safe_merge(Estado, {
            'id': data['id'],
            'nome': data['nome'],
            'uf': data['uf'],
            'ibge': data['ibge'],
            'excluido': data.get('excluido', False)
        })

    def inserir_unidade(self, item: Optional[dict]):
        if not item:
            return

        self.safe_merge(Unidade, {
            'id': item['id'],
            'nome': item['nome'],
            'excluido': item.get('excluido')
        })

    def inserir_classe(self, item: Optional[dict]):
        if not item:
            return

        self.safe_merge(Classe, {
            'id': item['id'],
            'nome': item['nome'],
            'excluido': item.get('excluido')
        })

    def inserir_tabela(self, item: Optional[dict]):
        if not item:
            return

        self.safe_merge(Tabela, {
            'id': item['id'],
            'nome': item['nome'],
            'id_estado': item['idEstado'],
            'mes': item['mes'],
            'ano': item['ano'],
            'data_hora_atualizacao': item['dataHoraAtualizacao'],
            'id_tipo_tabela': item['idTipoTabela'],
            'excluido': item.get('excluido')
        })

    def inserir_insumo_item(self, item: dict):
        # Persistir dependências primeiro
        if item.get('unidade'):
            self.inserir_unidade(item['unidade'])
        if item.get('tabela'):
            self.inserir_tabela(item['tabela'])
        if item.get('classe'):
            self.inserir_classe(item['classe'])

        # Certificar que a classe existe
        if 'idClasse' in item:
            classe_id = item['idClasse']
            if not self.session.get(Classe, classe_id):
                raise ValueError(f"Classe {classe_id} não encontrada para insumo {item['id']}")

        # Preparar dados do insumo
        insumo_data = {
            'id': item['id'],
            'nome': item['nome'],
            'codigo': item['codigo'],
            'id_tabela': item['idTabela'],
            'id_unidade': item['idUnidade'],
            'id_classe': item.get('idClasse'),
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

        self.safe_merge(InsumoComposicaoTabela, insumo_data)

    def inserir_composicoes_insumo(self, insumo_composicao_api: dict):
        if not insumo_composicao_api.get('insumoItem'):
            return

        self.inserir_insumo_item(insumo_composicao_api['insumoItem'])

        composicao_data = {
            'id': insumo_composicao_api['id'],
            'id_insumo': insumo_composicao_api['idInsumo'],
            'id_insumo_item': insumo_composicao_api['idInsumoItem'],
            'valor_onerado': insumo_composicao_api['valorOnerado'],
            'valor_nao_onerado': insumo_composicao_api['valorNaoOnerado'],
            'coeficiente': insumo_composicao_api['coeficiente'],
            'excluido': insumo_composicao_api.get('excluido')
        }

        self.safe_merge(ComposicaoItem, composicao_data)

    def inserir_composicao(self, i: Dict[str, Any]):

        try:
            # Persistir dependências primeiro com flush explícito
            if i.get('unidade'):
                self.inserir_unidade(i['unidade'])
            if i.get('tabela'):
                self.inserir_tabela(i['tabela'])
            if i.get('classe'):
                self.inserir_classe(i['classe'])

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

                model_class = model_map[field]
                if not self.session.get(model_class, value):
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

            self.safe_merge(InsumoComposicaoTabela, composicao_data)

            # Processar itens da composição
            for insumo_composicao in i.get('insumosComposicoes', []):
                self.inserir_composicoes_insumo(insumo_composicao)

            return True

        except Exception as e:
            self.session.rollback()
            print(f"Erro ao processar composição {i.get('id')}: {str(e)}")
            return False

    def commit(self):
        self.session.commit()

async def cadastrar_composicoes():
    with SessionLocal() as session:
        processor = Processor(session)

        async for item in get_insumos_or_compositions():
            composicao_data = item.model_dump()
            try:
                success = processor.inserir_composicao(composicao_data)
                if success:
                    processor.commit()
                    print(f"Composição {composicao_data['id']} inserida com sucesso")
                else:
                    print(
                        f"Falha ao inserir composição {composicao_data['id']} "
                        f"data: {json.dumps(composicao_data, indent=4)}"
                    )
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
