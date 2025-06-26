import asyncio
from typing import Type, TypeVar, Generic, Optional, Any, Dict
from sqlalchemy.orm import Session
# from sqlalchemy.exc import InvalidRequestError, IntegrityError
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
except Exception:
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






T = TypeVar('T')

class BaseRepository(Generic[T]):
    def __init__(self, session: Session, model: Type[T]):
        self.session = session
        self.model = model

    def get_by_id(self, entity_id) -> Optional[T]:
        return self.session.get(self.model, entity_id)

    def save(self, instance: T) -> T:
        self.session.merge(instance)
        self.session.flush()
        return instance

    def update(self, entity_id, **kwargs) -> Optional[T]:
        instance = self.get_by_id(entity_id)
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            self.session.flush()
        return instance

    def delete(self, entity_id) -> bool:
        instance = self.get_by_id(entity_id)
        if instance:
            self.session.delete(instance)
            self.session.flush()
            return True
        return False


class EstadoRepository(BaseRepository[Estado]):
    def __init__(self, session):
        super().__init__(session, Estado)

class UnidadeRepository(BaseRepository[Unidade]):
    def __init__(self, session):
        super().__init__(session, Unidade)

class ClasseRepository(BaseRepository[Classe]):
    def __init__(self, session):
        super().__init__(session, Classe)

class TabelaRepository(BaseRepository[Tabela]):
    def __init__(self, session):
        super().__init__(session, Tabela)

class InsumoComposicaoTabelaRepository(BaseRepository[InsumoComposicaoTabela]):
    def __init__(self, session):
        super().__init__(session, InsumoComposicaoTabela)

class ComposicaoItemRepository(BaseRepository[ComposicaoItem]):
    def __init__(self, session):
        super().__init__(session, ComposicaoItem)





class Processor:
    def __init__(self, session):
        self.session = session
        self.estado_repo = EstadoRepository(session)
        self.unidade_repo = UnidadeRepository(session)
        self.classe_repo = ClasseRepository(session)
        self.tabela_repo = TabelaRepository(session)
        self.insumo_repo = InsumoComposicaoTabelaRepository(session)
        self.composicao_item_repo = ComposicaoItemRepository(session)

    def assert_classe(self, classe_id):
        if not self.classe_repo.get_by_id(classe_id):
            classe = Classe(id=classe_id, nome="[CLASSIFICAR]")
            self.classe_repo.save(classe)
            self.session.flush()

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
        if item.get('unidade'):
            self.inserir_unidade(item['unidade'])
        if item.get('tabela'):
            self.inserir_tabela(item['tabela'])
        if item.get('classe'):
            self.inserir_classe(item['classe'])

        self.assert_classe(item['idClasse'])

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

            self.assert_classe(required_deps['id_classe'])

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
