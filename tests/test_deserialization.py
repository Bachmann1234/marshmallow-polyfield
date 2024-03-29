from marshmallow import Schema, ValidationError, post_load, fields
from marshmallow_polyfield.polyfield import PolyField, PolyFieldBase
import pytest
from tests.shapes import (
    Shape,
    Rectangle,
    Triangle,
    shape_schema_serialization_disambiguation,
    shape_property_schema_serialization_disambiguation,
    shape_schema_deserialization_disambiguation,
    shape_property_schema_deserialization_disambiguation,
    fuzzy_schema_deserialization_disambiguation,
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
        def make_object(self, data, **_):
            return TestPolyField.ContrivedShapeClass(
                data.get('main'),
                data.get('others')
            )

    class FuzzySchema(Schema):
        data = PolyField(
            deserialization_schema_selector=fuzzy_schema_deserialization_disambiguation,
            many=True
        )

    class ContrivedShapeSubclassSchema(Schema):
        main = ShapePolyField(required=True)
        others = ShapePolyField(allow_none=True, many=True)

        @post_load
        def make_object(self, data, **_):
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

        data = schema().load(
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

        data = schema().load(
            {'main': {'color': 'blue',
                      'length': 1,
                      'width': 100},
             'others': None}
        )
        assert data == original

    @with_all(
        ContrivedShapeClassSchema,
        ContrivedShapeSubclassSchema,
    )
    def test_deserailize_polyfield_none_required(self, schema):
        with pytest.raises(ValidationError):
            schema().load(
                {'main': None,
                 'others': None}
            )

    @with_all(
        ContrivedShapeClassSchema,
        ContrivedShapeSubclassSchema,
    )
    def test_deserialize_polyfield_invalid_type_error(self, schema):
        with pytest.raises(ValidationError) as excinfo:
            schema().load(
                {'main': {'color': 'blue', 'something': 4},
                 'others': None}
            )

        assert str(excinfo.value) == str("{'main': ['Could not detect type. "
                                         "Did not have a base or a length. "
                                         "Are you sure this is a shape?']}")

    @with_all(
        ContrivedShapeClassSchema,
        ContrivedShapeSubclassSchema,
    )
    def test_deserialize_polyfield_invalid_validation_error(self, schema):
        with pytest.raises(ValidationError) as excinfo:
            schema().load(
                {'main': {'base': -1, 'something': 4},
                 'others': None}
            )

        assert str(excinfo.value) == "{'main': ['Base cannot be negative.']}"

    @with_all(
        ContrivedShapeClassSchema,
        ContrivedShapeSubclassSchema,
    )
    def test_deserialize_polyfield_invalid_generic_error(self, schema):
        err_msg = 'Ensure there is a deserialization_schema_selector'
        with pytest.raises(ValidationError, match=err_msg):
            schema().load(
                {'main': {'width': 100, 'length': -1},
                 'others': {'width': 100, 'length': 10}}

            )

    @with_all(
        BadContrivedClassSchema,
        BadContrivedSubclassSchema,
    )
    def test_deserialize_polyfield_invalid_schema_returned_is_invalid(self, schema):
        with pytest.raises(ValidationError):
            schema().load(
                {'main': {'color': 'blue', 'something': 4},
                 'others': None}
            )

    @with_all(
        ContrivedShapeClassSchema,
        ContrivedShapeSubclassSchema,
    )
    def test_deserialize_polyfield_errors(self, schema):
        with pytest.raises(ValidationError):
            schema().load(
                {'main': {'color': 'blue', 'length': 'four', 'width': 4},
                 'others': None}
            )

    def test_fuzzy_schema(self):
        color = 'cyan'
        email = 'dummy@example.com'
        expected_data = {'data': [Shape(color), email]}

        data = self.FuzzySchema().load({'data': [{'color': color}, email]})

        assert data == expected_data


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
        def make_object(self, data, **_):
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
        def make_object(self, data, **_):
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
            [Rectangle('pink', 4, 93), Rectangle('red', 3, 90)],
            'rectangle'
        )

        data = schema().load(
            {'main': {'color': 'blue',
                      'length': 1,
                      'width': 100},
             'others': [
                 {'color': 'pink',
                  'length': 4,
                  'width': 93},
                 {'color': 'red',
                  'length': 3,
                  'width': 90}],
             'type': 'rectangle'}
        )
        assert data == original


def test_deserialize_polyfield_partial_loading():

    class CircleSchema(Schema):
        color = fields.Str(required=True)
        radius = fields.Int(required=True)

    class PartialLoadingShapeSchema(Schema):
        shape = PolyField(
            deserialization_schema_selector=lambda _, __: CircleSchema,
            required=True
        )

    data = {'shape': {'radius': 1}}

    assert PartialLoadingShapeSchema().load(data, partial=True) == data
    assert PartialLoadingShapeSchema(partial=True).load(data) == data
    assert PartialLoadingShapeSchema().load(data, partial=("shape.color", )) == data
