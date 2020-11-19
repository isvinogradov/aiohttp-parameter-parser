# URL query string / path parameter parser and validator for `aiohttp` views

[![pypi](https://img.shields.io/pypi/v/aiohttp-parameter-parser.svg)](https://pypi.python.org/pypi/aiohttp-parameter-parser)

Declare and validate HTTP query and path parameters in `aiohttp` views. 
Receive intended types instead of default `str`.  
Currently only path and URL query parameter location are supported.

### Basic usage examples:
```python
from datetime import datetime
from typing import Optional

import pytz
from aiohttp import web

from aiohttp_parameter_parser import ParameterView


class ExampleView(ParameterView):
    date_format = "%d-%m-%Y"  # custom date format for date parameters
    tz = pytz.timezone("Europe/Berlin")  # custom timezone for date parameters

    async def get(self) -> web.Response:
        my_tuple_of_ints: tuple[int, ...] = self.query_parameter(
            "parameter_name_in_request",
            required=True,
            is_array=True,
            max_items=6,  # len() restriction for list
            is_int=True,
            max_value=1337,  # maximum allowed value for array items
        )
        # If provided parameter is of wrong type or missing, a default 
        # HTTP 400 response is returned to client.
        
        my_str: Optional[str] = self.path_parameter(
            "a_string_parameter_name",
            # str is a default type for parsed parameter, so no 
            # `is_string=True` flag can be used
            choices=["foo", "bar", "baz"],  # enum
        )

        my_datetime: Optional[datetime] = self.query_parameter(
            "my_datetime_parameter",
            is_date=True,
        )  # will use custom timezone and date format provided above

        return web.json_response({
            "received_array_of_ints": my_tuple_of_ints,
            "received_str": my_str,
            "received_datetime": my_datetime.strftime(self.date_format),
        })
```

### Custom error response example
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
