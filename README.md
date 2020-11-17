# aiohttp-parameter-parser

Declare and validate HTTP query and path parameters in `aiohttp` views.
Currently only path and URL query parameter location are supported.

Example usage:

```python
from aiohttp import web

from aiohttp_parameter_parser import ParameterView


class ExampleHandler(ParameterView):
    async def get(self) -> web.Response:
        my_array_of_ints: int = self.query_parameter(
            "parameter_name_in_request",
            required=True,
            is_array=True,
            is_int=True,
        )
        # If provided parameter is of wrong type or missing, 
        # a default HTTP 400 response is returned to client.

        return web.json_response({"received_param": my_array_of_ints})
```