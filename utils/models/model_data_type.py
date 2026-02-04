from decimal import Decimal
import json
from functools import lru_cache
from typing import Any, TypeVar
from bson.regex import Regex as BsonRegex
from bson.objectid import ObjectId as BsonObjectId
from bson.timestamp import Timestamp as BsonTimestamp
from bson.decimal128 import Decimal128 as BsonDecimal128
from fastapi.encoders import ENCODERS_BY_TYPE, jsonable_encoder
from pydantic import BaseModel as _BaseModel, ConfigDict, Field, GetJsonSchemaHandler
from pydantic_core import core_schema
from pydantic.json_schema import JsonSchemaValue
from base64 import standard_b64encode

class ObjectId(BsonObjectId):

    invalid_object_id = "invalid_object_id"
    
    @classmethod
    def __get_pydantic_core_schema__(
        cls, *args, **kwargs
    ) -> core_schema.CoreSchema:
        
        def validate_from_str(value: str) -> ObjectId:
            try:
                result = ObjectId(value)
            except:
                raise ValueError("Invalid ObjectId")
            return result

        from_str_schema = core_schema.chain_schema(
            [
                core_schema.no_info_plain_validator_function(validate_from_str),
            ]
        )

        def validate_from_BsonObjectId(value: BsonObjectId) -> ObjectId:
            try:
                result = ObjectId(value)
            except:
                raise ValueError("Invalid ObjectId")
            return result
        
        from_BsonObjectId_schema = core_schema.chain_schema(
            [
                core_schema.is_instance_schema(BsonObjectId),
                core_schema.no_info_plain_validator_function(validate_from_BsonObjectId),
            ]
        )

        def serialize(value: Any, info: core_schema.SerializationInfo) -> str | ObjectId:
            if info.mode == 'json':
                return str(value)
            else:
                return ObjectId(value)

        return core_schema.json_or_python_schema(
            json_schema=from_str_schema,
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(ObjectId),
                    from_BsonObjectId_schema,
                    from_str_schema,
                ],
                custom_error_message="Bukan object Id",
                custom_error_type=ObjectId.invalid_object_id
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                serialize,
                info_arg=True,
                when_used='always',
            ),
            ref="ObjectId"
        )
    
    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        json_schema = handler(core_schema.str_schema())
        json_schema.update(
            type="string",
            description="ObjectId",
            examples=["000000000000000000000000"],
            example="000000000000000000000000"
        )
        return json_schema
    
class Decimal128(BsonDecimal128):

    @classmethod
    def __get_pydantic_core_schema__(
        cls, *args, **kwargs
    ) -> core_schema.CoreSchema:
        
        def validate_from_any(v: Any) -> Decimal128:
            if isinstance(v, BsonDecimal128):
                return v # type: ignore
            if isinstance(v, Decimal128):
                return v
            return Decimal128(v)
        
        from_decimal_schema = core_schema.chain_schema(
            [
                core_schema.decimal_schema(
                    allow_inf_nan=False,
                    max_digits=18,
                    decimal_places=2
                ),
                core_schema.no_info_plain_validator_function(validate_from_any),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=core_schema.decimal_schema(
                allow_inf_nan=False,
                max_digits=18,
                decimal_places=2
            ),
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(BsonDecimal128),
                    from_decimal_schema,
                ],
                custom_error_message="Format angka tidak didukung (16:2)",
                custom_error_type="InvalidDecimal"
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: Decimal128.decimal_encoder(instance),
                when_used="json"
            )
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        json_schema = handler(_core_schema)
        json_schema.update(
            type="string",
            description="Decimal String 16:2",
            examples=["123456.45"],
            example="123456.45",
        )
        return json_schema
    
    @staticmethod
    def decimal_encoder(val: 'Decimal128 | BsonDecimal128 | int | float | Decimal') -> Decimal:
        """Encode Decimal128/BsonDecimal128 or numeric types to Decimal for JSON serialization."""
        try:
            # BsonDecimal128 and Decimal128 have to_decimal()
            if hasattr(val, "to_decimal"):
                return val.to_decimal()
            # Decimal or numeric types
            if isinstance(val, Decimal):
                return val
            if isinstance(val, (int, float)):
                return Decimal(str(val))
            # Fallback: attempt Decimal conversion
            return Decimal(val)
        except Exception as err:
            # As a last resort, raise a clear error
            raise TypeError(f"Cannot encode value {val!r} as Decimal: {err}")

class BaseModel(_BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        use_attribute_docstrings=True
    )
    
    @classmethod
    @lru_cache(maxsize=None)
    def Projection(cls):
        return {s if m.alias is None else m.alias: 1 for s, m in cls.model_fields.items()}
    
    @classmethod
    def model_validate(
        cls,
        obj: Any,
        *,
        strict: bool | None = None,
        from_attributes: bool | None = None,
        context: dict[str, Any] | None = None,
    ) -> 'BaseModel':
        try:
            ret = super().model_validate(obj, strict=strict, from_attributes=from_attributes, context=context)
            return ret
        except Exception as err:
            print("model_validate error:", err)
            raise err
        
    @classmethod
    def model_validate_json(
        cls,
        json_data: str | bytes | bytearray,
        *,
        strict: bool | None = None,
        context: dict[str, Any] | None = None,
    ) -> 'BaseModel':
        try:
            ret = super().model_validate_json(json_data, strict=strict, context=context)
            return ret
        except Exception as err:
            print("model_validate_json error:", err)
            raise err
        
    def MsJsonString(self) -> str:
        d = self.model_dump(mode="json")
        return json.dumps(
            jsonable_encoder(d),
            sort_keys=True,
            indent=0,
            separators=None
        )

class BaseModelObjectId(BaseModel):
    id: ObjectId = Field(
        default=...,
        alias="_id"
    )

@lru_cache(maxsize=None)
def GetProjection(_cls: BaseModel) -> dict[str, int]: # type: ignore
    if isinstance(_cls, BaseModel):
        return _cls.Projection()

def BsonTimestampIsoFormat(o: BsonTimestamp) -> str:
    return o.as_datetime().isoformat()
    
def BsonRegexEncode(r: BsonRegex) -> dict[str, Any]:
    return {
        "pattern": r.pattern,
        "flags": r.flags
    }

def Byte_Encode(b: bytes) -> str | None:
    if b:
        return standard_b64encode(b).decode(encoding="ascii")
    else:
        return None
    
ENCODERS_BY_TYPE[ObjectId] = str
ENCODERS_BY_TYPE[BsonObjectId] = str
ENCODERS_BY_TYPE[BsonTimestamp] = BsonTimestampIsoFormat
ENCODERS_BY_TYPE[BsonRegex] = BsonRegexEncode
ENCODERS_BY_TYPE[bytes] = Byte_Encode
ENCODERS_BY_TYPE[Decimal128] = Decimal128.decimal_encoder
ENCODERS_BY_TYPE[BsonDecimal128] = Decimal128.decimal_encoder

TBaseModelObjectId = TypeVar("TBaseModelObjectId", bound=BaseModelObjectId)
TGenericBaseModel = TypeVar("TGenericBaseModel", bound=BaseModel)
