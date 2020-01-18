from collections import namedtuple

from marshmallow import Schema, fields
import pytest

from marshmallow_polyfield import PolyFieldBase, ExplicitPolyField

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
        super().__init__(many=many, **metadata)

        self.bad_string_value = bad_string_value

    def serialization_schema_selector(self, value, obj):
        return BadStringValueModifierSchema()

    def deserialization_schema_selector(self, value, obj):
        return BadStringValueModifierSchema()

    def serialization_value_modifier(self, value, obj):
        return {'a': self.bad_string_value}

    def deserialization_value_modifier(self, value, obj):
        return {'a': self.bad_string_value}


explicit_poly_field_with_overrides = ExplicitPolyField(
    class_to_schema_mapping={
        str: fields.String,
        int: fields.Integer,
        dict: fields.Dict,
    },
    class_to_name_overrides={
        str: 'str',
    },
)


explicit_poly_field_without_overrides = ExplicitPolyField(
    class_to_schema_mapping={
        int: fields.Integer,
        dict: fields.Dict,
    },
)


ExplicitPolyFieldExample = namedtuple(
    'ExplicitPolyFieldExample',
    [
        'type_name',
        'value',
        'layer',
        'field',
        'polyfield',
    ],
)


def create_explicit_poly_field_example(type_name, value, field, polyfield):
    return ExplicitPolyFieldExample(
        type_name=type_name,
        value=value,
        layer={'type': type_name, 'value': value},
        field=field,
        polyfield=polyfield,
    )


parametrize_explicit_poly_field_type_name_and_value = pytest.mark.parametrize(
    ['example'],
    [
        [create_explicit_poly_field_example(
            type_name=u'str',
            value=u'red',
            field=fields.String,
            polyfield=explicit_poly_field_with_overrides,
        )],
        [create_explicit_poly_field_example(
            type_name=u'int',
            value=42,
            field=fields.Integer,
            polyfield=explicit_poly_field_with_overrides,
        )],
        [create_explicit_poly_field_example(
            type_name=u'dict',
            value={u'puppy': 3.9},
            field=fields.Dict,
            polyfield=explicit_poly_field_with_overrides,
        )],
        [create_explicit_poly_field_example(
            type_name=u'int',
            value=42,
            field=fields.Integer,
            polyfield=explicit_poly_field_without_overrides,
        )],
        [create_explicit_poly_field_example(
            type_name=u'dict',
            value={u'puppy': 3.9},
            field=fields.Dict,
            polyfield=explicit_poly_field_without_overrides,
        )],
    ],
)
