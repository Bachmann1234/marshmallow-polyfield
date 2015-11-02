from marshmallow import Schema, ValidationError, post_load
from marshmallow_polyfield.polyfield import PolyField
import pytest
from tests.shapes import (
    shape_schema_serialization_disambiguation,
    Rectangle,
    Triangle,
    shape_schema_deserialization_disambiguation
)


def _bad_deserializer_disambiguation(self):
        return 1


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

    def test_deserialize_polyfield(self):
        original = self.ContrivedShapeClass(
            Rectangle('blue', 1, 100),
            [Rectangle('pink', 4, 93), Triangle('red', 8, 45)]
        )

        data, errors = self.ContrivedShapeClassSchema(strict=True).load(
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

    def test_deserialize_polyfield_none(self):
        original = self.ContrivedShapeClass(
            Rectangle("blue", 1, 100),
            None
        )

        data, errors = self.ContrivedShapeClassSchema(strict=True).load(
            {'main': {'color': 'blue',
                      'length': 1,
                      'width': 100},
             'others': None}
        )
        assert not errors
        assert data == original

    def test_deserailize_polyfield_none_required(self):
        with pytest.raises(ValidationError):
            self.ContrivedShapeClassSchema(strict=True).load(
                {'main': None,
                 'others': None}
            )

    def test_deserialize_polyfield_invalid(self):
        with pytest.raises(ValidationError):
            self.ContrivedShapeClassSchema(strict=True).load(
                {'main': {'color': 'blue', 'something': 4},
                 'others': None}
            )

    def test_deserialize_polyfield_invalid_schema_returned_is_invalid(self):
        with pytest.raises(ValidationError):
            self.BadContrivedClassSchema(strict=True).load(
                {'main': {'color': 'blue', 'something': 4},
                 'others': None}
            )

    def test_deserialize_polyfield_errors(self):
        data, errors = self.ContrivedShapeClassSchema().load(
            {'main': {'color': 'blue', 'length': 'four', 'width': 4},
             'others': None}
        )
        assert errors
