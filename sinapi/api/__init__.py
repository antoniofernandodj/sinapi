from copy import deepcopy
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, Generator, List, Optional
import httpx

try:
    from api import schema
except:
    from sinapi.api import schema


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(Path(__file__).name)


class SinapiService:
    __instance = None
    TIMEOUT = 3600

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, login, token):
        self.email = login
        self.token = token
        self.url_base = "https://api.apisinapi.com.br/"

    async def login(self) -> schema.AuthData:
        if self.auth_data and self._is_token_valid():
            logger.debug("Using cached token")
            return self.auth_data

        url = "api/Authentication/login"
        json = {"login": self.email, "senha": self.token}
        request = await self.http_client.post(url=url, json=json)

        data = request.json()

        auth_data = schema.AuthData(
            token=data["token"], expires=data["expires"], usuario=data["usuario"]
        )

        self.auth_data = auth_data
        logger.debug("Got new token")
        return auth_data

    async def insumos(
        self,
        tipo_tabela: Optional[str] = None,
        ano: Optional[str] = None,
        mes: Optional[int] = None,
        uf: Optional[str] = None,
        nome_classe: Optional[str] = None,
        nome_unidade: Optional[str] = None,
        composicao: Optional[bool] = None,
        term: Optional[str] = None,
        order: Optional[str] = None,
        direction: Optional[str] = None,
        search_type: Optional[str] = None,
        page: Optional[int] = 1,
        limit: Optional[int] = 10,
    ) -> schema.InsumosResponse:
        """
        Realiza uma requisição GET ao endpoint /api/Insumos da API para obter uma lista de insumos.

        Args:
            tipo_tabela (str): SINAPI ou SICRO.
            ano (int): Ano para o filtro.
            mes (int): Mês para o filtro.
            uf (str): Unidade federativa (ex: RS).
            nome_classe (str): Termo para busca no campo Classe.
            nome_unidade (str): Termo para busca no campo Unidade.
            composicao (bool): True para filtrar por composições, False para não composições.
            term (str): Termo de busca genérico.
            order (str): Campo de ordenação (ex: nome).
            direction (str): Sentido de ordenação (asc ou desc).
            search_type (str): Tipo de busca (contains, starts_with, etc).
            page (int): Número da página de resultados.
            limit (int): Limite de resultados por página.

        Returns:
            dict: Dicionário com a resposta JSON da API.
        """
        params = self.__remove_none({
            "TipoTabela": tipo_tabela,
            "Ano": ano,
            "Mes": mes,
            "Uf": uf,
            "NomeClasse": nome_classe,
            "NomeUnidade": nome_unidade,
            "Composicao": composicao,
            "Term": term,
            "Order": order,
            "Direction": direction,
            "SearchType": search_type,
            "Page": page,
            "Limit": limit,
        })

        response = await self._make_request("GET", url="api/Insumos", params=params)

        data = response.json()

        return schema.InsumosResponse(items=data["items"], totalRows=data["totalRows"])

    async def insumos_todos(
        self,
        tipo_tabela: Optional[str] = None,
        ano: Optional[str] = None,
        mes: Optional[int] = None,
        uf: Optional[str] = None,
        nome_classe: Optional[str] = None,
        nome_unidade: Optional[str] = None,
        composicao: Optional[bool] = None,
        term: Optional[str] = None,
        order: Optional[str] = None,
        direction: Optional[str] = None,
        search_type: Optional[str] = None,
    ) -> AsyncGenerator[schema.InsumosResponse, Any]:
        
        params = self.__remove_none({
            "TipoTabela": tipo_tabela,
            "Ano": ano,
            "Mes": mes,
            "Uf": uf,
            "NomeClasse": nome_classe,
            "NomeUnidade": nome_unidade,
            "Composicao": composicao,
            "Term": term,
            "Order": order,
            "Direction": direction,
            "SearchType": search_type,
            "Page": 1,
            "Limit": 50,
        })

        results: List[schema.InsumosResponseItem] = []
        loop = True
        while loop:
            response = await self._make_request("GET", url="api/Insumos", params=params)
            data = response.json()
            result = schema.InsumosResponse(items=data["items"], totalRows=data["totalRows"])
            yield result
            loop = bool(result.items)
            if result.items:
                results.extend(result.items)
                params['Page'] += 1

    async def estados(
        self,
        term: Optional[str] = None,
        order: Optional[str] = None,
        direction: Optional[str] = None,
        search_type: Optional[str] = None,
        page: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> schema.EstadoResponse:
        """
        Obtém uma lista de estados com base nos parâmetros de busca e ordenação.

        Args:
            term (str): Termo de busca que será aplicado de acordo com o tipo de busca definido em `search_type`.
            order (str): Campo para ordenação dos resultados.
            direction (str): Sentido da ordenação dos resultados. Valores possíveis:
                - "asc": Crescente
                - "desc": Decrescente
            search_type (str): Tipo de busca aplicado ao campo `term`. Valores possíveis:
                - "contains": Contém o termo
                - "starts_with": Começa com o termo
                - "ends_with": Termina com o termo
                - "equals": Igual ao termo
            page (int): Número da página a ser retornada.
            limit (int): Número máximo de resultados por página. Para desabilitar paginação, defina um valor alto, como 9999999.

        Returns:
            dict: Um dicionário contendo os resultados da consulta de estados.
        """

        params = self.__remove_none({
            "Term": term,
            "Order": order,
            "Direction": direction,
            "SearchType": search_type,
            "Page": page,
            "Limit": limit,
        })

        response = await self._make_request(
            "GET",
            url="api/Estados",
            params=params,
        )

        return schema.EstadoResponse(**response.json())

    async def tabelas(
        self,
        ano: Optional[int] = None,
        mes: Optional[int] = None,
        uf: Optional[str] = None,
        term: Optional[str] = None,
        order: Optional[str] = None,
        direction: Optional[str] = None,
        search_type: Optional[str] = None,
        page: Optional[int] = 0,
        limit: Optional[int] = 10,
    ):
        """
        Retorna todas as tabelas, as quais são atualizadas mensalmente,
        e possuem informações de acordo com o estado (UF).

        Args:
            ano (int): Ano para o filtro.
            mes (int): Mês para o filtro.
            uf (str): Unidade federativa (ex: RS).
            term (str): Termo de busca.
            order (str): Campo para ordenação (ex: nome).
            direction (str): Sentido da ordenação (asc ou desc).
            search_type (str): Tipo de busca (contains, starts_with, etc).
            page (int): Número da página de resultados.
            limit (int): Limite de resultados por página.

        Returns:
            schema.TabelasResponse: Um objeto com os resultados da consulta.
        """
        params = self.__remove_none({
            "Ano": ano,
            "Mes": mes,
            "Uf": uf,
            "Term": term,
            "Order": order,
            "Direction": direction,
            "SearchType": search_type,
            "Page": page,
            "Limit": limit,
        })

        response = await self._make_request("GET", url="api/Tabelas", params=params)
        data = response.json()
        return schema.TabelasResponse(items=data["items"], totalRows=data["totalRows"])

    async def anos_importados(
        self,
        tipo_tabela: Optional[str] = None,
        uf: Optional[str] = None,
        ano: Optional[str] = None,
    ) -> schema.AnosResponse:
        """
        Retorna uma lista de anos que foram importados, informando Tipo de Tabela e UF.

        Args:
            tipo_tabela (str): Tipo da tabela (ex: SINAPI).
            uf (str): Unidade federativa (ex: RS).

        Returns:
            schema.AnosImportadosResponse: Um objeto com os anos importados.
        """
        params = self.__remove_none({
            "TipoTabela": tipo_tabela,
            "Uf": uf, "Ano": ano
        })

        response = await self._make_request(
            "GET", url="api/Tabelas/anos/select", params=params
        )

        data = response.json()

        return schema.AnosResponse(anos=[schema.Ano(**item) for item in data])

    async def meses_importados(
        self,
        tipo_tabela: Optional[str] = None,
        uf: Optional[str] = None,
        ano: Optional[str] = None,
    ) -> List[schema.Mes]:
        """
        Retorna uma lista de meses que foram importados, informando Tipo de Tabela, UF e Ano.

        Args:
            tipo_tabela (str): Tipo da tabela (ex: SINAPI ou SICRO).
            uf (str): Unidade federativa (ex: RS).
            ano (str): Ano para filtrar os meses.

        Returns:
            List[schema.Mes]: Uma lista de objetos com os meses importados.
        """
        params = self.__remove_none({
            "TipoTabela": tipo_tabela,
            "Uf": uf,
            "Ano": ano,
        })

        response = await self._make_request(
            "GET", url="api/Tabelas/meses/select", params=params
        )

        return [schema.Mes(**item) for item in response.json()]

    def _is_token_valid(self) -> bool:
        if self.auth_data is None:
            return False

        date_str = self.auth_data.expires
        fixed_date_str = date_str
        if "." in date_str:
            date_part, time_part = date_str.split(".")
            time_fraction, offset = time_part.split("+")
            time_fraction = time_fraction[:6]
            fixed_date_str = f"{date_part}.{time_fraction}+{offset}"

        expiry_time = datetime.fromisoformat(fixed_date_str)
        return datetime.now(timezone.utc) < expiry_time

    async def _make_request(
        self,
        method: str,
        url: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> httpx.Response:

        try:
            callable = getattr(self.http_client, method.lower())
            kwargs = await self._make_request_settings(
                url=url, json=json, data=data, params=params
            )

            response: httpx.Response = await callable(**kwargs)
            logging.debug(response)
            logging.debug(response.json())
            response.raise_for_status()  # Raises an exception for HTTP errors
            return response

        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error occurred: {e.response.status_code} - {e.response.text}"
            )
            raise

        except httpx.RequestError as e:
            logger.error(f"Request error occurred: {e}")
            raise

    async def _make_request_settings(self, **kw):
        authorization = await self.login()

        # url: str
        # json: Optional[Dict[str, Any]]
        # data: Optional[Any]
        kwargs = self.__remove_none({
            **deepcopy(kw),
            "headers": {"Authorization": f"Bearer {authorization.token}"},
        })

        return kwargs

    @property
    def auth_data(self) -> Optional[schema.AuthData]:
        try:
            return self.__auth_data  # type: ignore
        except Exception:
            return None

    @auth_data.setter
    def auth_data(self, item: schema.AuthData):
        self.__auth_data = item

    async def __aenter__(self):
        self.http_client = await httpx.AsyncClient(
            base_url=self.url_base,
            timeout=SinapiService.TIMEOUT
        ).__aenter__()

        logger.debug("Opening SinapiService")
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.http_client.__aexit__()
        logger.debug("Closing SinapiService")


    def __remove_none(self, params: dict):
        return {k: v for k, v in params.items() if v is not None}