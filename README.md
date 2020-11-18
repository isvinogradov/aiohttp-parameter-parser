# aiohttp-parameter-parser

[![pypi](https://img.shields.io/pypi/v/aiohttp-parameter-parser.svg)](https://pypi.python.org/pypi/aiohttp-parameter-parser)

Declare and validate HTTP query and path parameters in `aiohttp` views.
Currently only path and URL query parameter location are supported.

Basic usage:
```python
from aiohttp import web

from aiohttp_parameter_parser import ParameterView


class ExampleView(ParameterView):
    async def get(self) -> web.Response:
        my_array_of_ints = self.query_parameter(
            "parameter_name_in_request",
            required=True,
            is_array=True,
            is_int=True,
        )
        # If provided parameter is of wrong type or missing, 
        # a default HTTP 400 response is returned to client.

        return web.json_response({"received_param": my_array_of_ints})
```

How to return custom response when parameter validation fails:
```python
from aiohttp import web

from aiohttp_parameter_parser import ParameterView


class CustomErrorResponseView(ParameterView):
    def validation_error_handler(self, msg: str) -> web.Response:
        # just override this method of base class
        # 'msg' is a human-readable explanation of validation error
        j = {
            "ok": False,
            "data": None,
            "error": {
                "description": msg,
            },
        }
        # you can use raise or return here
        return web.json_response(status=418, data=j)
```
