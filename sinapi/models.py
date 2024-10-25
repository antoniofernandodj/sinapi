from typing import Optional
from pydantic import BaseModel
from sqlalchemy import Column, Integer, Text, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from sinapi.api.schema import (
    InsumosResponseItem,
    InsumosResponseTabela,
    InsumosResponseUnidade,
    InsumosResponseClasse,
    InsumosResponseItem,
)


from sqlalchemy.orm import Mapped


Base = declarative_base()


class Estado(Base):
    __tablename__ = "estados"

    id = Column(Integer, primary_key=True)
    nome = Column(Text, nullable=False)
    uf = Column(Text, nullable=False)
    ibge = Column(Integer, nullable=False)
    excluido = Column(Boolean, default=False)

    def __hash__(self):
        return hash(self.id)

    def to_pydantic(self):
        try:
            from sinapi.api.schema import EstadoResponseItem
        except:
            from api.schema import EstadoResponseItem

        return EstadoResponseItem(
            id=self.id,  #  type: ignore
            nome=self.nome,  #  type: ignore
            uf=self.uf,  #  type: ignore
            ibge=self.ibge,  #  type: ignore
            excluido=self.excluido,  #  type: ignore
        )


class Tabela(Base):
    __tablename__ = "tabelas"
    id = Column(Integer, primary_key=True)
    nome = Column(Text)
    id_estado = Column(Integer, ForeignKey("estados.id"), nullable=False)
    mes = Column(Integer)
    ano = Column(Integer)
    data_hora_atualizacao = Column(Text)
    id_tipo_tabela = Column(Integer)
    excluido = Column(Boolean, nullable=True)

    estado = relationship("Estado")

    def to_pydantic(self) -> InsumosResponseTabela:

        return InsumosResponseTabela.model_validate(
            {
                "id": self.id,
                "nome": self.nome,
                "idEstado": self.id_estado,
                "mes": self.mes,
                "ano": self.ano,
                "dataHoraAtualizacao": self.data_hora_atualizacao,
                "idTipoTabela": self.id_tipo_tabela,
                "excluido": self.excluido,
                "estado": self.estado.to_pydantic(),
                "tipoTabela": str(self.id_tipo_tabela),
            }
        )


class Unidade(Base):
    __tablename__ = "unidades"
    id = Column(Integer, primary_key=True)
    nome = Column(Text)
    excluido = Column(Boolean, nullable=True)

    def to_pydantic(self) -> InsumosResponseUnidade:
        return InsumosResponseUnidade.model_validate(
            {
                "id": self.id,
                "nome": self.nome,
                "excluido": self.excluido,
            }
        )


class Classe(Base):
    __tablename__ = "classes"
    id = Column(Integer, primary_key=True)
    nome = Column(Text)
    excluido = Column(Boolean, nullable=True)

    def to_pydantic(self) -> InsumosResponseClasse:
        return InsumosResponseClasse.model_validate(
            {
                "id": self.id,
                "nome": self.nome,
                "excluido": self.excluido,
            }
        )


class InsumoTabela(Base):
    __tablename__ = "insumos_tabela"
    id = Column(Integer, primary_key=True)
    nome = Column(Text)
    codigo = Column(Text)
    id_tabela = Column(Integer, ForeignKey("tabelas.id"))
    id_unidade = Column(Integer, ForeignKey("unidades.id"))
    id_classe = Column(Integer, nullable=True)
    valor_onerado = Column(Float)
    valor_nao_onerado = Column(Float)
    composicao = Column(Boolean)
    percentual_mao_de_obra = Column(Float)
    percentual_material = Column(Float)
    percentual_equipamentos = Column(Float)
    percentual_servicos_terceiros = Column(Float)
    percentual_outros = Column(Float)
    excluido = Column(Boolean, nullable=True)

    tabela: Mapped["Tabela"] = relationship(foreign_keys=[id_tabela])
    unidade: Mapped["Unidade"] = relationship(foreign_keys=[id_unidade])
    # classe: Mapped["Classe"] = relationship(foreign_keys=[id_classe])

    insumos_composicoes = relationship(
        "InsumoComposicao", back_populates="insumo_tabela"
    )

    def to_pydantic(self) -> InsumosResponseItem:
        insumo_dict = InsumosResponseItem.model_validate(
            {
                "id": self.id,
                "nome": self.nome,
                "codigo": self.codigo,
                "idTabela": self.id_tabela,
                "idUnidade": self.id_unidade,
                "idClasse": self.id_classe,
                "composicao": self.composicao,
                "percentualMaoDeObra": self.percentual_mao_de_obra,
                "percentualMaterial": self.percentual_material,
                "percentualEquipamentos": self.percentual_equipamentos,
                "percentualServicosTerceiros": self.percentual_servicos_terceiros,
                "percentualOutros": self.percentual_outros,
                "excluido": self.excluido,
                "valorOnerado": self.valor_onerado,
                "valorNaoOnerado": self.valor_nao_onerado,
                "tabela": self.tabela.to_pydantic() if self.tabela else None,
                "unidade": self.unidade.to_pydantic() if self.unidade else None,
                # "classe": self.classe.to_pydantic() if self.classe else None,
                "classe": None,
                "insumosComposicoes": (
                    [
                        insumo_comp.to_pydantic()
                        for insumo_comp in self.insumos_composicoes
                    ]
                    if self.insumos_composicoes
                    else []
                ),
                # "insumosComposicoes": []
            }
        )

        return InsumosResponseItem.model_validate(insumo_dict)


class ComposicaoTabela(Base):
    __tablename__ = "composicoes_tabela"
    id = Column(Integer, primary_key=True)
    nome = Column(Text)
    codigo = Column(Text)
    id_tabela = Column(Integer, ForeignKey("tabelas.id"))
    id_unidade = Column(Integer, ForeignKey("unidades.id"))
    id_classe = Column(Integer, nullable=True)
    valor_onerado = Column(Float)
    valor_nao_onerado = Column(Float)
    composicao = Column(Boolean)
    percentual_mao_de_obra = Column(Float)
    percentual_material = Column(Float)
    percentual_equipamentos = Column(Float)
    percentual_servicos_terceiros = Column(Float)
    percentual_outros = Column(Float)
    excluido = Column(Boolean, nullable=True)

    # tabela = relationship("Tabela")
    # unidade = relationship("Unidade")
    # classe = relationship("Classe")

    composicoes_composicoes = relationship(
        "InsumoComposicao", back_populates="composicoes"
    )

    def to_pydantic(self) -> InsumosResponseItem:
        return InsumosResponseItem.model_validate(
            {
                "id": self.id,
                "nome": self.nome,
                "codigo": self.codigo,
                "idTabela": self.id_tabela,
                "idUnidade": self.id_unidade,
                "idClasse": self.id_classe,
                "valorOnerado": self.valor_onerado,
                "valorNaoOnerado": self.valor_nao_onerado,
                "composicao": self.composicao,
                "percentualMaoDeObra": self.percentual_mao_de_obra,
                "percentualMaterial": self.percentual_material,
                "percentualEquipamentos": self.percentual_equipamentos,
                "percentualServicosTerceiros": self.percentual_servicos_terceiros,
                "percentualOutros": self.percentual_outros,
                "excluido": self.excluido,
                "insumosComposicoes": (
                    [
                        composicao.to_pydantic()
                        for composicao in self.composicoes_composicoes
                    ]
                    if self.composicoes_composicoes
                    else []
                ),
            }
        )


class InsumoItem(Base):
    __tablename__ = "insumo_items"
    id = Column(Integer, primary_key=True)
    nome = Column(Text)
    codigo = Column(Text)
    id_tabela = Column(Integer, ForeignKey("tabelas.id"))
    id_unidade = Column(Integer, ForeignKey("unidades.id"))
    id_classe = Column(Integer, nullable=True)
    valor_onerado = Column(Float)
    valor_nao_onerado = Column(Float)
    composicao = Column(Boolean, nullable=True)
    percentual_mao_de_obra = Column(Float, nullable=True)
    percentual_material = Column(Float, nullable=True)
    percentual_equipamentos = Column(Float, nullable=True)
    percentual_servicos_terceiros = Column(Float, nullable=True)
    percentual_outros = Column(Float, nullable=True)
    excluido = Column(Boolean, nullable=True)

    # tabela = relationship("Tabela")
    # unidade = relationship("Unidade")
    # classe = relationship("Classe")

    def to_pydantic(self) -> InsumosResponseItem:
        return InsumosResponseItem.model_validate(
            {
                "id": self.id,
                "nome": self.nome,
                "codigo": self.codigo,
                "idTabela": self.id_tabela,
                "idUnidade": self.id_unidade,
                "idClasse": self.id_classe,
                "valorOnerado": self.valor_onerado,
                "valorNaoOnerado": self.valor_nao_onerado,
                "composicao": self.composicao,
                "percentualMaoDeObra": self.percentual_mao_de_obra,
                "percentualMaterial": self.percentual_material,
                "insumosComposicoes": [],
                "percentualEquipamentos": self.percentual_equipamentos,
                "percentualServicosTerceiros": self.percentual_servicos_terceiros,
                "percentualOutros": self.percentual_outros,
                "excluido": self.excluido,
            }
        )


class ComposicaoItem(Base):
    __tablename__ = "composicao_items"
    id = Column(Integer, primary_key=True)
    nome = Column(Text)
    codigo = Column(Text)
    id_tabela = Column(Integer, ForeignKey("tabelas.id"))
    id_unidade = Column(Integer, ForeignKey("unidades.id"))
    valor_onerado = Column(Float)
    valor_nao_onerado = Column(Float)
    composicao = Column(Boolean, nullable=True)
    percentual_mao_de_obra = Column(Float, nullable=True)
    percentual_material = Column(Float, nullable=True)
    percentual_equipamentos = Column(Float, nullable=True)
    percentual_servicos_terceiros = Column(Float, nullable=True)
    percentual_outros = Column(Float, nullable=True)
    excluido = Column(Boolean, nullable=True)

    # tabela = relationship("Tabela")
    # unidade = relationship("Unidade")
    # classe = relationship("Classe")


class InsumoComposicaoResponse(BaseModel):
    id: int
    id_insumo_item: int
    valor_onerado: float
    valor_nao_onerado: float
    coeficiente: float

    id_insumo: Optional[int] = None
    id_composicao: Optional[int] = None
    excluido: Optional[bool] = None

    insumo_item: Optional[InsumosResponseItem] = None


class InsumoComposicao(Base):
    __tablename__ = "insumo_composicoes"
    id = Column(Integer, primary_key=True)
    id_insumo = Column(Integer, ForeignKey("insumos_tabela.id"), nullable=True)
    id_composicao = Column(Integer, ForeignKey("composicoes_tabela.id"), nullable=True)
    id_insumo_item = Column(Integer, ForeignKey("insumo_items.id"))
    valor_onerado = Column(Float)
    valor_nao_onerado = Column(Float)
    coeficiente = Column(Float)
    excluido = Column(Boolean, nullable=True)

    insumo_tabela = relationship("InsumoTabela", back_populates="insumos_composicoes")
    composicoes = relationship(
        "ComposicaoTabela", back_populates="composicoes_composicoes"
    )
    insumo_item = relationship("InsumoItem")

    def to_pydantic(
        self, insumo_item: Optional[InsumosResponseItem] = None
    ) -> InsumoComposicaoResponse:
        return InsumoComposicaoResponse.model_validate(
            {
                "id": self.id,
                "id_insumo": self.id_insumo,
                "id_composicao": self.id_composicao,
                "id_insumo_item": self.id_insumo_item,
                "insumo_item": insumo_item,
                "valor_onerado": self.valor_onerado,
                "valor_nao_onerado": self.valor_nao_onerado,
                "coeficiente": self.coeficiente,
                "excluido": self.excluido,
            }
        )
