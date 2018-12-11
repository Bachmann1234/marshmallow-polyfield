from marshmallow import Schema, ValidationError, post_load, fields
from marshmallow_polyfield.polyfield import PolyField, PolyFieldBase
import pytest
from tests.shapes import (
    Rectangle,
    Triangle,
    shape_schema_serialization_disambiguation,
    shape_property_schema_serialization_disambiguation,
    shape_schema_deserialization_disambiguation,
    shape_property_schema_deserialization_disambiguation
)
from tests.polyclasses import (
    ShapePolyField,
    ShapePropertyPolyField,
    with_all
)


def _bad_deserializer_disambiguation(self, _):
        return 1


class BadClassPolyField(PolyFieldBase):
    def serialization_schema_selector(self, value, obj):
        return _bad_deserializer_disambiguation(value, obj)

    def deserialization_schema_selector(self, value, obj):
        return _bad_deserializer_disambiguation(value, obj)


class TestPolyField(object):

    class BadContrivedClassSchema(Schema):
        main = PolyField(
            serialization_schema_selector=_bad_deserializer_disambiguation,
            deserialization_schema_selector=_bad_deserializer_disambiguation,
            required=True
        )
        others = PolyField(
            serialization_schema_selector=_bad_deserializer_disambiguation,
            deserialization_schema_selector=_bad_deserializer_disambiguation,
            allow_none=True,
            many=True
        )

    class BadContrivedSubclassSchema(Schema):
        main = BadClassPolyField(required=True)
        others = BadClassPolyField(allow_none=True, many=True)

    class ContrivedShapeClass(object):
        def __init__(self, main, others):
            self.main = main
            self.others = others

        def __eq__(self, other):
            return self.__dict__ == other.__dict__

    class ContrivedShapeClassSchema(Schema):
        main = PolyField(
            serialization_schema_selector=shape_schema_serialization_disambiguation,
            deserialization_schema_selector=shape_schema_deserialization_disambiguation,
            required=True
        )
        others = PolyField(
            serialization_schema_selector=shape_schema_serialization_disambiguation,
            deserialization_schema_selector=shape_schema_deserialization_disambiguation,
            allow_none=True,
            many=True
        )

        @post_load
        def make_object(self, data):
            return TestPolyField.ContrivedShapeClass(
                data.get('main'),
                data.get('others')
            )

    class ContrivedShapeSubclassSchema(Schema):
        main = ShapePolyField(required=True)
        others = ShapePolyField(allow_none=True, many=True)

        @post_load
        def make_object(self, data):
            return TestPolyField.ContrivedShapeClass(
                data.get('main'),
                data.get('others')
            )

    @with_all(
        ContrivedShapeClassSchema,
        ContrivedShapeSubclassSchema,
    )
    def test_deserialize_polyfield(self, schema):
        original = self.ContrivedShapeClass(
            Rectangle('blue', 1, 100),
            [Rectangle('pink', 4, 93), Triangle('red', 8, 45)]
        )

        data, errors = schema(strict=True).load(
            {'main': {'color': 'blue',
                      'length': 1,
                      'width': 100},
             'others': [
                 {'color': 'pink',
                  'length': 4,
                  'width': 93},
                 {'color': 'red',
                  'base': 8,
                  'height': 45}]}
        )
        assert not errors
        assert data == original

    @with_all(
        ContrivedShapeClassSchema,
        ContrivedShapeSubclassSchema,
    )
    def test_deserialize_polyfield_none(self, schema):
        original = self.ContrivedShapeClass(
            Rectangle("blue", 1, 100),
            None
        )

        data, errors = schema(strict=True).load(
            {'main': {'color': 'blue',
                      'length': 1,
                      'width': 100},
             'others': None}
        )
        assert not errors
        assert data == original

    @with_all(
        ContrivedShapeClassSchema,
        ContrivedShapeSubclassSchema,
    )
    def test_deserailize_polyfield_none_required(self, schema):
        with pytest.raises(ValidationError):
            schema(strict=True).load(
                {'main': None,
                 'others': None}
            )

    @with_all(
        ContrivedShapeClassSchema,
        ContrivedShapeSubclassSchema,
    )
    def test_deserialize_polyfield_invalid(self, schema):
        with pytest.raises(ValidationError):
            schema(strict=True).load(
                {'main': {'color': 'blue', 'something': 4},
                 'others': None}
            )

    @with_all(
        BadContrivedClassSchema,
        BadContrivedSubclassSchema,
    )
    def test_deserialize_polyfield_invalid_schema_returned_is_invalid(self, schema):
        with pytest.raises(ValidationError):
            schema(strict=True).load(
                {'main': {'color': 'blue', 'something': 4},
                 'others': None}
            )

    @with_all(
        ContrivedShapeClassSchema,
        ContrivedShapeSubclassSchema,
    )
    def test_deserialize_polyfield_errors(self, schema):
        data, errors = schema().load(
            {'main': {'color': 'blue', 'length': 'four', 'width': 4},
             'others': None}
        )
        assert errors


class TestPolyFieldDisambiguationByProperty(object):

    class ContrivedShapeClass(object):
        def __init__(self, main, others, type):
            self.main = main
            self.others = others
            self.type = type

        def __eq__(self, other):
            return self.__dict__ == other.__dict__

    class ContrivedShapeClassSchema(Schema):
        main = PolyField(
            serialization_schema_selector=shape_property_schema_serialization_disambiguation,
            deserialization_schema_selector=shape_property_schema_deserialization_disambiguation,
            required=True
        )
        others = PolyField(
            serialization_schema_selector=shape_property_schema_serialization_disambiguation,
            deserialization_schema_selector=shape_property_schema_deserialization_disambiguation,
            allow_none=True,
            many=True
        )
        type = fields.String(required=True)

        @post_load
        def make_object(self, data):
            return TestPolyFieldDisambiguationByProperty.ContrivedShapeClass(
                data.get('main'),
                data.get('others'),
                data.get('type')
            )

    class ContrivedShapeSubclassSchema(Schema):
        main = ShapePropertyPolyField(required=True)
        others = ShapePropertyPolyField(allow_none=True, many=True)
        type = fields.String(required=True)

        @post_load
        def make_object(self, data):
            return TestPolyFieldDisambiguationByProperty.ContrivedShapeClass(
                data.get('main'),
                data.get('others'),
                data.get('type')
            )

    @with_all(
        ContrivedShapeClassSchema,
        ContrivedShapeSubclassSchema,
    )
    def test_deserialize_polyfield(self, schema):
        original = self.ContrivedShapeClass(
            Rectangle('blue', 1, 100),
            [Rectangle('pink', 4, 93)],
            'rectangle'
        )

        data, errors = schema(strict=True).load(
            {'main': {'color': 'blue',
                      'length': 1,
                      'width': 100},
             'others': [{'color': 'pink',
                         'length': 4,
                         'width': 93}],
             'type': 'rectangle'}
        )
        assert not errors
        assert data == original
