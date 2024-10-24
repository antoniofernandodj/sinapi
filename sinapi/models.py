from sqlalchemy import Column, Integer, Text, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Estado(Base):
    __tablename__ = 'estados'
    
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
            excluido=self.excluido  #  type: ignore
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


class Unidade(Base):
    __tablename__ = "unidades"
    id = Column(Integer, primary_key=True)
    nome = Column(Text)
    excluido = Column(Boolean, nullable=True)


class Classe(Base):
    __tablename__ = "classes"
    id = Column(Integer, primary_key=True)
    nome = Column(Text)
    excluido = Column(Boolean, nullable=True)


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

    # tabela = relationship("Tabela")
    # unidade = relationship("Unidade")
    # classe = relationship("Classe")

    insumos_composicoes = relationship("InsumoComposicao", back_populates="insumo")


class ComposicaoTabela(Base):
    __tablename__ = "composicoes_tabela"
    id = Column(Integer, primary_key=True)
    nome = Column(Text)
    codigo = Column(Text)
    # id_tabela = Column(
    #     Integer, nullable=True
    # )
    id_tabela = Column(Integer, ForeignKey("tabelas.id"))
    # id_unidade = Column(
    #     Integer, nullable=True
    # )
    id_unidade = Column(Integer, ForeignKey("unidades.id"))
    id_classe = Column(
        Integer, nullable=True
    )  # Column(Integer, ForeignKey("classes.id"))
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

    composicoes_composicoes = relationship("InsumoComposicao", back_populates="composicoes")


class InsumoItem(Base):
    __tablename__ = "insumo_items"
    id = Column(Integer, primary_key=True)
    nome = Column(Text)
    codigo = Column(Text)
    # id_tabela = Column(
    #     Integer, nullable=True
    # )
    id_tabela = Column(Integer, ForeignKey("tabelas.id"))
    # id_unidade = Column(
    #     Integer, nullable=True
    # )
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


class ComposicaoItem(Base):
    __tablename__ = "composicao_items"
    id = Column(Integer, primary_key=True)
    nome = Column(Text)
    codigo = Column(Text)
    # id_tabela = Column(
    #     Integer, nullable=True
    # )
    id_tabela = Column(Integer, ForeignKey("tabelas.id"))
    # id_unidade = Column(
    #     Integer, nullable=True
    # )
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

    insumo = relationship("InsumoTabela", back_populates="insumos_composicoes")
    composicoes = relationship("ComposicaoTabela", back_populates="composicoes_composicoes")
    insumo_item = relationship("InsumoItem")
