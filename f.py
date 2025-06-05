from functools import wraps
from typing import Callable, Union, cast
from quart import Quart, Blueprint, g, request
import inspect


app = Quart(__name__)


from typing import Protocol, Callable, runtime_checkable, Any


@runtime_checkable
class RouteHandler(Protocol):
    _route: str
    _methods: list[str]
    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...



class Base:
    _blueprint: Blueprint

    @classmethod
    def register_all(cls, app: Union[Quart, Blueprint]):
        self = cls()

        async def before_all_requests():
            if (handler := getattr(self, "on_request", None)):
                if inspect.iscoroutinefunction(handler):
                    await handler()
                else:
                    handler()


        self._blueprint.before_request(before_all_requests)

        def make_view_func(endpoint):
            @wraps(endpoint)
            async def view_func(*args, **kwargs):
                return await endpoint(*args, **kwargs)
            return view_func

        for endpoint_name in dir(self):
            if endpoint_name == 'register_all' or endpoint_name.startswith('_'):
                continue
            endpoint = getattr(self, endpoint_name)

            if callable(endpoint) and hasattr(endpoint, '_route'):
                self._blueprint.add_url_rule(
                    endpoint._route,
                    endpoint.__name__,
                    view_func=make_view_func(endpoint),
                    methods=endpoint._methods
                )

        app.register_blueprint(self._blueprint)


def controller(base_route):
    def decorator(cls):
        blueprint = Blueprint(cls.__name__, __name__, url_prefix=base_route)

        class Cls(Base, cls):
            def __init__(self) -> None:
                super().__init__()

        Cls._blueprint = blueprint
        return Cls
    return decorator


def path(route: str, methods: Union[str, list[str]] = ['GET']):
    def decorator(func: Callable):
        if isinstance(methods, str):
            _methods = [methods]
        else:
            _methods = methods

        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        wrapped = cast(RouteHandler, wrapper)
        wrapped._route = route
        wrapped._methods = _methods

        return wrapped

    return decorator


# -------------------------
# 🎯 Exemplo de Controlador
# -------------------------

@controller('/users')
class Users:

    def __init__(self):
        print('Inicializando Users...')
        self.nome = 'João'
        self.dados = 'Empresa XPTO'

    async def on_request(self):
        print('🔄 Executando antes de qualquer endpoint de Users')
        g.request_id = request.headers.get('X-Request-ID', 'undefined')


    @path('/id/<int:id>', methods='GET')
    async def present(self, id):
        return {
            "mensagem": f"Olá, meu ID é {id}",
            "request_id": g.request_id,
            "nome": self.nome
        }

    @path('/about', methods='GET')
    async def about(self):
        return {
            "sobre": f"Sobre a empresa: {self.dados}"
        }


# -------------------------
# 🔥 Registrar e Rodar
# -------------------------

Users.register_all(app)

if __name__ == '__main__':
    app.run(debug=True)
