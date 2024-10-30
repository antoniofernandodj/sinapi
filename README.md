# Insumo e Composição Data Insertion Script

## Introdução

Este módulo Python automatiza o processo de download, carregamento e inserção de dados relacionados a insumos e composições no banco de dados MySQL. Ele garante que os dados sejam atualizados no banco de dados, seja pela inserção de novos registros ou atualização de registros existentes, utilizando a abordagem session.merge() do SQLAlchemy para combinar a lógica de inserção e atualização de maneira eficiente.

O script manipula arquivos JSON que contêm os dados de insumos e composições e realiza as seguintes operações:

1. Baixa os dados dos insumos e composições de uma fonte externa.
2. Insere ou atualiza os registros nas tabelas correspondentes no banco de dados MySQL.
3. Cria automaticamente o banco de dados "insumos", caso ele ainda não exista.

O script foi projetado para garantir que os dados estejam sempre sincronizados e atualizados no banco de dados MySQL, usando SQLAlchemy para ORM (Object Relational Mapping).

Requisitos
- UV (Gerenciador de dependencias do python)
- Python 3.x
- MySQL Server

## Instalação

### Passos

1. Certifique-se de ter o Python 3.x instalado.

2. Instale as dependências necessárias executando:

```bash
uv sync
```

3. Configure o MySQL e certifique-se de que as credenciais de acesso estejam corretas.
O banco de dados será criado automaticamente se ainda não existir.

### Estrutura do Banco de Dados
O banco de dados consiste nas seguintes tabelas:

- Tabela: Armazena as informações sobre as tabelas de preços, incluindo dados de estado, mês, ano e outros.
- Classe: Armazena as classes dos insumos.
- Unidade: Armazena as unidades de medida dos insumos e composições.
- Insumo: Contém os dados dos insumos.
- Composicao: Contém os dados das composições, que podem incluir insumos.
- InsumoItem: Representa os itens de insumos associados a composições ou insumos.
- ComposicaoMontada: Faz a ligação entre os insumos e as composições.

### Funcionalidades

#### 1. Criação do Banco de Dados
Ao iniciar o script, o banco de dados MySQL será automaticamente criado caso ainda não exista. Isso é feito com a seguinte instrução SQL:

```python
with create_engine(SGBD_URL, echo=True).connect() as connection:
    connection.execute(text("CREATE DATABASE IF NOT EXISTS insumos"))
```

Em seguida, o script conecta-se ao banco de dados recém-criado e utiliza o SQLAlchemy para mapear e criar as tabelas automaticamente a partir das definições do modelo:

```python
engine = create_engine(DATABASE_INSUMOS_URL, echo=True)
Base.metadata.create_all(engine)
```

#### 2. Download de Dados
Os dados de insumos e composições são baixados utilizando a função download_insumos_or_compositions (definida no módulo web). Este processo ocorre de forma assíncrona para otimizar o desempenho e evitar bloqueios durante a execução:

```python
asyncio.run(download_insumos_or_compositions(INSUMOS_FILE, composicao=False))
```

A função acima baixa o arquivo insumos.json, enquanto a seguinte faz o download do arquivo de composições:

```python
asyncio.run(download_insumos_or_compositions(COMPOSICOES_FILE, composicao=True))
```

#### 3. Inserção de Dados
Os dados são carregados a partir dos arquivos JSON usando a função load_json, que lê e carrega o conteúdo dos arquivos para inserção no banco de dados:

```python
def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
```

#### 4. Inserção e Atualização de Tabelas, Classes e Unidades
As funções inserir_tabelas, inserir_classes, e inserir_unidades inserem ou atualizam os registros das tabelas correspondentes. Caso os registros já existam, eles são atualizados utilizando session.merge(), que verifica a existência e faz o "merge" dos dados:

```python
def inserir_tabelas(data):
    for item in data:
        tabela = Tabela(
            id=item["tabela"]["id"],
            nome=item["tabela"]["nome"],
            ...
        )
        session.merge(tabela)
    session.commit()
```

O mesmo processo é repetido para classes e unidades.

#### 5. Inserção e Atualização de Insumos e Composições
As funções inserir_insumos e inserir_composicoes cuidam da inserção ou atualização dos registros de insumos e composições, utilizando também o método merge do SQLAlchemy. O processo de inserção cuida de garantir que todos os dados relacionados, como unidades, tabelas e classes, sejam inseridos ou atualizados corretamente antes de inserir os próprios insumos ou composições:

```python
def main_insert(i, Model: Union[Type[Insumo], Type[Composicao]]):
    inserir_unidade(i["unidade"])
    inserir_tabela(i["tabela"])
    inserir_classe(i["classe"])
    item = Model(
        id=i["id"],
        nome=i["nome"],
        codigo=i["codigo"],
        ...
    )
    session.merge(item)
    session.commit()
    session.refresh(item)
    inserir_composicoes_insumo(i['insumosComposicoes'], item)
```

#### 6. Inserção de Itens de Composição e Insumos
A função inserir_insumo_item cuida de inserir os itens individuais de insumos e composições. Ela também garante que os relacionamentos entre insumos e composições sejam mantidos corretamente através da tabela de associação ComposicaoMontada:

```python
def inserir_insumo_item(item: Optional[dict], composicao_item, insumo: Union[Insumo, Composicao]):
    ...
    insumo_composicao = ComposicaoMontada(
        id=composicao_item["id"],
        id_insumo=insumo.id,
        id_composicao=None,
        id_insumo_item=insumo_item.id,
        ...
    )
    session.merge(insumo_composicao)
    session.commit()
```

### Execução
Para executar o script, basta rodar o módulo principal:

```bash
uv run python sinapi
```

O script será responsável por:

- Criar o banco de dados insumos, caso ele não exista.
- Fazer o download dos dados de insumos e composições.
- Inserir ou atualizar os dados no banco de dados.

### Estrutura dos Arquivos
`insumos.json`: Contém os dados dos insumos, como código, nome, valores, unidades, classes, etc.
`composicoes.json`: Contém os dados das composições, que são formadas por múltiplos insumos.

### Conclusão
Este módulo facilita o processo de sincronização de dados entre os arquivos JSON e o banco de dados MySQL. Ele foi projetado para garantir que os dados estejam sempre atualizados, evitando duplicidades e garantindo a consistência.