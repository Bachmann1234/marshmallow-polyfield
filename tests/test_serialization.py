from collections import namedtuple
from marshmallow import fields, Schema
from marshmallow_polyfield.polyfield import PolyField
import pytest
from tests.shapes import (
    Rectangle,
    Triangle,
    shape_schema_serialization_disambiguation,
    shape_schema_deserialization_disambiguation,
)
from tests.polyclasses import ShapePolyField, with_all


def with_both_shapes(func):
    return with_all(
        PolyField(
            serialization_schema_selector=shape_schema_serialization_disambiguation,
            deserialization_schema_selector=shape_schema_deserialization_disambiguation
        ),
        ShapePolyField()
    )(func)


def test_serializing_named_tuple():
    Point = namedtuple('Point', ['x', 'y'])

    field = fields.Field()

    p = Point(x=4, y=2)

    assert field.serialize('x', p) == 4


def test_serializing_named_tuple_with_meta():
    Point = namedtuple('Point', ['x', 'y'])
    p = Point(x=4, y=2)

    class PointSerializer(Schema):
        class Meta:
            fields = ('x', 'y')

    serialized = PointSerializer().dump(p)
    assert serialized.data['x'] == 4
    assert serialized.data['y'] == 2


@with_both_shapes
def test_serializing_polyfield_rectangle(field):
    rect = Rectangle("blue", 4, 10)
    Sticker = namedtuple('Sticker', ['shape', 'image'])
    marshmallow_sticker = Sticker(rect, "marshmallow.png")
    rect_dict = field.serialize('shape', marshmallow_sticker)

    assert rect_dict == {"length": 4, "width": 10, "color": "blue"}


@with_both_shapes
def test_serializing_polyfield_None(field):
    Sticker = namedtuple('Sticker', ['shape', 'image'])
    marshmallow_sticker = Sticker(None, "marshmallow.png")
    rect_dict = field.serialize('shape', marshmallow_sticker)

    assert rect_dict is None


@with_all(
    PolyField(
        serialization_schema_selector=shape_schema_serialization_disambiguation,
        deserialization_schema_selector=shape_schema_deserialization_disambiguation,
        many=True
    ),
    ShapePolyField(many=True)
)
def test_serializing_polyfield_many(field):
    rect = Rectangle("blue", 4, 10)
    tri = Triangle("red", 1, 100)
    StickerCollection = namedtuple('StickerCollection', ['shapes', 'image'])
    marshmallow_sticker_collection = StickerCollection([rect, tri], "marshmallow.png")
    shapes = field.serialize('shapes', marshmallow_sticker_collection)
    expected_shapes = [
        {"length": 4, "width": 10, "color": "blue"},
        {"base": 1, "height": 100, "color": "red"}
    ]
    assert shapes == expected_shapes


@with_both_shapes
def test_invalid_polyfield(field):
    Sticker = namedtuple('Sticker', ['shape', 'image'])
    with pytest.raises(TypeError):
        field.serialize('shape', Sticker(3, 3))


@with_both_shapes
def test_serializing_polyfield_by_parent_type(field):
    rect = Rectangle("blue", 4, 10)
    Sticker = namedtuple('Sticker', ['shape', 'image', 'type'])
    marshmallow_sticker = Sticker(rect, "marshmallow.png", 'rectangle')
    rect_dict = field.serialize('shape', marshmallow_sticker)

    assert rect_dict == {"length": 4, "width": 10, "color": "blue"}
