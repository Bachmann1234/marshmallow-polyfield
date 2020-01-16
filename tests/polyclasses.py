from marshmallow_polyfield import PolyFieldBase
from marshmallow import Schema, fields

from tests.shapes import (
    shape_schema_serialization_disambiguation,
    shape_property_schema_serialization_disambiguation,
    shape_schema_deserialization_disambiguation,
    shape_property_schema_deserialization_disambiguation
)


def with_all(*args):
    def wrapper(func):
        def wrapped(*args_):
            return [
                func(*(args_ + (a,)))
                for a in args
            ]
        return wrapped
    return wrapper


class ShapePolyField(PolyFieldBase):
    def serialization_schema_selector(self, value, obj):
        return shape_schema_serialization_disambiguation(value, obj)

    def deserialization_schema_selector(self, value, obj):
        return shape_schema_deserialization_disambiguation(value, obj)


class ShapePropertyPolyField(PolyFieldBase):
    def serialization_schema_selector(self, value, obj):
        return shape_property_schema_serialization_disambiguation(value, obj)

    def deserialization_schema_selector(self, value, obj):
        return shape_property_schema_deserialization_disambiguation(value, obj)


class BadStringValueModifierSchema(Schema):
    a = fields.String()


class BadStringValueModifierPolyField(PolyFieldBase):
    def __init__(self, bad_string_value, many=False, **metadata):
        super(BadStringValueModifierPolyField, self).__init__(
            many=many,
            **metadata
        )

        self.bad_string_value = bad_string_value

    def serialization_schema_selector(self, value, obj):
        return BadStringValueModifierSchema()

    def deserialization_schema_selector(self, value, obj):
        return BadStringValueModifierSchema()

    def serialization_value_modifier(self, value, obj):
        return {'a': self.bad_string_value}

    def deserialization_value_modifier(self, value, obj):
        return {'a': self.bad_string_value}
