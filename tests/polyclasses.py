from marshmallow_polyfield import PolyFieldBase

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
