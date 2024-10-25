from __future__ import annotations

from datetime import datetime
from token import OP
from typing import Any, List, Optional

from pydantic import BaseModel



def to_camel_case(string: str) -> str:
    parts = string.split('_')
    return parts[0] + ''.join(word.capitalize() for word in parts[1:])



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

    def __eq__(self, other):
        return isinstance(other, EstadoResponseItem) and self.id == other.id and self.ibge == other.ibge

    def __hash__(self):
        return hash((self.id, self.ibge))


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
    composicao: Any
    percentualMaoDeObra: Any
    percentualMaterial: Any
    percentualEquipamentos: Any
    percentualServicosTerceiros: Any
    percentualOutros: Any
    excluido: Any
    insumosComposicoes: List[Any]
    valorOnerado: Optional[float] = None
    valorNaoOnerado: Optional[float] = None
    tabela: Optional[InsumosResponseTabela] = None
    unidade: Optional[InsumosResponseUnidade] = None
    classe: Optional[InsumosResponseClasse] = None

    class Config:
        alias_generator = to_camel_case
        model_config = {
            'from_attributes': True
        }


class InsumosResponse(BaseModel):
    items: List[InsumosResponseItem]
    totalRows: int


class Tabela(BaseModel):
    id: int
    nome: str
    idEstado: int
    mes: int
    ano: int
    dataHoraAtualizacao: datetime
    idTipoTabela: int
    excluido: Optional[bool]
    estado: EstadoResponseItem
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
