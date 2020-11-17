from datetime import datetime
from decimal import Decimal
from typing import Optional, Union, Iterable, Any, Mapping

import pytz
from aiohttp import web

single_parameter_value = Union[None, str, int, Decimal, datetime]
validated_query_parameter = Union[
    None,
    single_parameter_value,
    tuple[single_parameter_value, ...],
]


class ConfigError(Exception):
    """ Invalid argument configuration """


class ValidationError(Exception):
    def __init__(self, msg: str):
        super().__init__()
        self.msg = msg


class ParameterView(web.View):
    date_format = "%Y-%m-%d"
    tz = pytz.timezone("UTC")

    def validation_error_handler(self, msg: str) -> None:
        """
        Override this method to perform custom action upon validation error
        (for example throw different exception)
        """
        raise web.HTTPBadRequest(text=msg)

    def query_parameter(self,
                        name_in_request: str,
                        *,
                        required: bool = False,
                        default: Any = None,
                        is_array: bool = False,
                        is_string: bool = True,
                        is_int: bool = False,
                        is_decimal: bool = False,
                        is_date: bool = False,
                        is_bool: bool = False,
                        min_value: Optional[int] = None,
                        max_value: Optional[int] = None,
                        min_length: Optional[int] = None,
                        max_length: Optional[int] = None,
                        min_items: Optional[int] = None,
                        max_items: Optional[int] = None,
                        choices: Optional[Iterable] = None,
                        choices_are_case_insensitive: bool = False,
                        choices_mapping: Optional[Mapping] = None) -> validated_query_parameter:
        valid_config = (is_int + is_decimal + is_date + is_bool) <= 1
        if not valid_config:
            raise ConfigError(
                "Invalid query parameter configuration: at most one flag "
                "in (is_int, is_decimal, is_date, is_bool) should be True",
            )

        if is_int or is_decimal or is_date or is_bool:
            is_string = False

        raw_value: Union[None, str] = self.request.rel_url.query.get(
            name_in_request,
        )
        if is_array:
            raw_value: Optional[list[str]] = self.request.query.getall(
                name_in_request, None,
            )

        try:
            return self._parse_parameter(
                raw_value,
                name_in_request,
                required=required,
                default=default,
                is_array=is_array,
                is_string=is_string,
                is_int=is_int,
                is_decimal=is_decimal,
                is_date=is_date,
                is_bool=is_bool,
                min_value=min_value,
                max_value=max_value,
                min_length=min_length,
                max_length=max_length,
                min_items=min_items,
                max_items=max_items,
                choices=choices,
            )
        except ValidationError as e:
            self.validation_error_handler(e.msg)

    def path_parameter(self,
                       name_in_path: str,
                       *,
                       required: bool = False,
                       default: Any = None,
                       is_string: bool = True,
                       is_int: bool = False,
                       min_length: Optional[int] = None,
                       max_length: Optional[int] = None,
                       min_value: Optional[int] = None,
                       max_value: Optional[int] = None,
                       choices: Optional[Iterable] = None) -> Union[str, int, None]:
        if is_int:
            is_string = False

        try:
            return self._parse_parameter(
                self.request.match_info.get(name_in_path, None),
                name_in_path,
                required=required,
                default=default,
                is_string=is_string,
                is_int=is_int,
                min_length=min_length,
                max_length=max_length,
                min_value=min_value,
                max_value=max_value,
                choices=choices,
            )
        except ValidationError as e:
            self.validation_error_handler(e.msg)

    def _parse_parameter(self,
                         raw_value: Union[None, str, Optional[list[str]]],
                         name_in_request: str,
                         *_,
                         **kwargs):
        if raw_value is None:
            if kwargs.get("required"):
                raise ValidationError(
                    f"<{name_in_request}> is a required query parameter",
                )
            else:
                # no need to validate empty parameter if it's optional
                return kwargs.get("default")

        if kwargs.get("is_array"):
            if kwargs.get("min_items") is not None \
                    and len(raw_value) < kwargs.get("min_items"):
                raise ValidationError(
                    f"Minimum array length for <{name_in_request}> "
                    f"is {kwargs['min_items']}",
                )
            if kwargs.get("max_items") is not None \
                    and len(raw_value) > kwargs.get("max_items"):
                raise ValidationError(
                    f"Maximum array length for <{name_in_request}> "
                    f"is {kwargs['max_items']}",
                )

            return tuple(
                self._convert_and_validate_single_value(
                    v,
                    name_in_request,
                    **kwargs,
                )
                for v in raw_value
            )
        return self._convert_and_validate_single_value(
            raw_value,
            name_in_request,
            **kwargs,
        )

    def _convert_and_validate_single_value(self,
                                           input_value: str,
                                           name_in_request: str,
                                           *,
                                           is_string: bool = True,
                                           is_int: bool = False,
                                           is_decimal: bool = False,
                                           is_date: bool = False,
                                           is_bool: bool = False,
                                           min_value: int = None,
                                           max_value: int = None,
                                           min_length: int = None,
                                           max_length: int = None,
                                           choices: Optional[Iterable] = None,
                                           **_):
        parsed_value = input_value

        # perform value conversion
        if is_string:
            pass  # is already a string
        if is_int:
            try:
                parsed_value = int(input_value)
            except (ValueError, TypeError):
                raise ValidationError(
                    f"Invalid <{name_in_request}> type (int is expected)",
                )
        elif is_decimal:
            try:
                parsed_value = Decimal(input_value)
            except (ValueError, TypeError):
                raise ValidationError(
                    f"Invalid <{name_in_request}> type (int/float is expected)",
                )
        elif is_date:
            try:
                dt = datetime.strptime(input_value, self.date_format)
                parsed_value = self.tz.localize(dt)
            except (ValueError, TypeError):
                raise ValidationError(
                    f"Invalid <{name_in_request}> type "
                    f"(date in {self.date_format} format  is expected)",
                )
        elif is_bool:
            if input_value.lower() in ("true", "1"):
                return True
            if input_value.lower() in ("false", "0"):
                return False
            raise ValidationError(
                f"<{name_in_request}> is a bool parameter; "
                f"allowed values are 1/true/TrUe/truE or 0/FALSE/False/false"
            )

        # validate minimums and maximums
        if not choices:  # if options provided, they override max/min constraints
            if is_int or is_decimal:
                # validate min and max values for numeric parameters
                if min_value is not None and parsed_value < min_value:
                    raise ValidationError(
                        f"Minimum value for <{name_in_request}> is {min_value}",
                    )

                if max_value is not None and parsed_value > max_value:
                    raise ValidationError(
                        f"Maximum value for <{name_in_request}> is {max_value}",
                    )

            else:  # validate length for strings
                if min_length is not None and len(parsed_value) < min_length:
                    raise ValidationError(
                        f"Minimum length for <{name_in_request}> is {min_length}",
                    )

                if max_length is not None and len(parsed_value) > max_length:
                    raise ValidationError(
                        f"Maximum length for <{name_in_request}> is {max_length}",
                    )

        # validate choices
        if choices and parsed_value not in choices:
            raise ValidationError(
                f"Possible values for parameter <{name_in_request}> are "
                f"{'/'.join(str(x) for x in choices)}",
            )

        return parsed_value
