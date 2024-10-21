from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel


class Permissao(BaseModel):
    id: int
    nome: str
    descricao: str
    excluido: Any
    permissoesTiposUsuarios: List
    permissoesUsuarios: List


class PermissoesTiposUsuario(BaseModel):
    id: int
    idPermissao: int
    idTipoUsuario: int
    permitido: bool
    permissao: Permissao


class TipoUsuario(BaseModel):
    id: int
    nome: str
    excluido: Any
    permissoesTiposUsuarios: List[PermissoesTiposUsuario]
    usuarios: List


class Pagamento(BaseModel):
    id: int
    idUsuario: int
    dataHoraInicio: str
    dataHoraFim: str
    dataHoraPagamento: str
    pago: bool
    excluido: Any


class Usuario(BaseModel):
    id: int
    nome: str
    sobrenome: str
    senha: str
    telefone: Any
    celular: str
    emailVerificado: bool
    idTipoUsuario: int
    email: str
    dataHoraUltimoAcesso: str
    excluido: Any
    tipoUsuario: TipoUsuario
    erros: List
    logs: List
    permissoesUsuarios: List
    pagamentos: List[Pagamento]


class AuthData(BaseModel):
    token: str
    expires: str
    usuario: Usuario


class EstadoResponseItem(BaseModel):
    id: int
    nome: str
    uf: str
    ibge: int
    excluido: Any


class EstadoResponse(BaseModel):
    items: List[EstadoResponseItem]
    totalRows: int


class InsumosResponseTabela(BaseModel):
    id: int
    nome: str
    idEstado: int
    mes: int
    ano: int
    dataHoraAtualizacao: str
    idTipoTabela: int
    excluido: Any
    estado: Any
    tipoTabela: Any


class InsumosResponseUnidade(BaseModel):
    id: int
    nome: str
    excluido: Any


class InsumosResponseClasse(BaseModel):
    id: int
    nome: str
    excluido: Any


class InsumosResponseItem(BaseModel):
    id: int
    nome: str
    codigo: str
    idTabela: int
    idUnidade: int
    idClasse: int
    valorNaoOnerado: float
    composicao: Any
    percentualMaoDeObra: Any
    percentualMaterial: Any
    percentualEquipamentos: Any
    percentualServicosTerceiros: Any
    percentualOutros: Any
    excluido: Any
    tabela: InsumosResponseTabela
    unidade: InsumosResponseUnidade
    classe: InsumosResponseClasse
    insumosComposicoes: List[Any]
    valorOnerado: Optional[float] = None


class InsumosResponse(BaseModel):
    items: List[InsumosResponseItem]
    totalRows: int


class EstadoTabelaResponse(BaseModel):
    id: int
    nome: str
    uf: str
    ibge: int
    excluido: Optional[bool]


class Tabela(BaseModel):
    id: int
    nome: str
    idEstado: int
    mes: int
    ano: int
    dataHoraAtualizacao: datetime
    idTipoTabela: int
    excluido: Optional[bool]
    estado: EstadoTabelaResponse
    tipoTabela: Optional[str]


class TabelasResponse(BaseModel):
    items: List[Tabela]
    totalRows: int


class Ano(BaseModel):
    disabled: bool
    group: Optional[str]  # Pode ser None
    selected: bool
    text: str
    value: str


class AnosResponse(BaseModel):
    anos: List[Ano]


class Mes(BaseModel):
    value: int
    text: str


class MesesResponse(BaseModel):
    meses: List[Mes]
