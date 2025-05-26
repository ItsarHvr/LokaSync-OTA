from typing import Any
from bson import ObjectId
from pydantic_core import core_schema


class PyObjectId(ObjectId):
    """
    A custom Pydantic-compatible ObjectId field to handle MongoDB's ObjectId.

    Provides:
    - Validation: Ensures that the ObjectId is valid.
    - Schema modification: Adjusts OpenAPI schema to treat the field as a string.
    """

    @classmethod
    def __get_validators__(cls):
        """Yield the validator for ObjectId to be used by Pydantic."""
        yield cls.validate

    @classmethod
    def validate(cls, v) -> ObjectId:
        """
        Validate that the input is a valid ObjectId.

        Args:
            v: The value to validate.
        Returns:
            A valid ObjectId.
        Raises:
            ValueError: If the ObjectId is invalid.
        """
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_core_schema__(
            cls, _source_type: Any, _handler: Any
    ) -> core_schema.CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId),
                core_schema.chain_schema([
                    core_schema.str_schema(),
                    core_schema.no_info_plain_validator_function(cls.validate),
                ])
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x)
            ),
        )
    
    class Config:
        """Configuration for the PyObjectId model."""
        json_encoders = {ObjectId: str}