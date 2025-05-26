import re
from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema


class Username(str):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        def validate(value: str) -> str:
            if re.fullmatch(r"^[a-zA-Z0-9_]{8,24}$", value):
                return value
            raise ValueError("Invalid username format")

        return core_schema.no_info_plain_validator_function(validate)
