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
        my_list_of_ints = self.query_parameter(
            "parameter_name_in_request",
            required=True,
            is_array=True,
            max_items=6,  # len() restriction for list
            is_int=True,
            max_value=1337,  # maximum allowed item value
        )
        # If provided parameter is of wrong type or missing, a default 
        # HTTP 400 response is returned to client.
        
        my_str = self.path_parameter(  # default type for parsed parameter is str
            "a_string_parameter_name",
            choices=["foo", "bar", "baz"],  # enum
        )
        return web.json_response({
            "received_array_of_ints": my_list_of_ints,
            "received_str": my_str,
        })
```

Sometimes you want to return custom error response instead of default HTTP 400.
Here's an example how to raise custom exception if validation fails: 
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
