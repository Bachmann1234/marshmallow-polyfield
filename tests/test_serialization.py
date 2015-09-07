from collections import namedtuple
from marshmallow import fields, Schema
from marshmallow_polyfield.polyfield import PolyField
import pytest
from tests.shapes import Rectangle, shape_schema_disambiguation, Triangle


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


def test_serializing_polyfield_rectangle():
    rect = Rectangle("blue", 4, 10)
    Sticker = namedtuple('Sticker', ['shape', 'image'])
    marshmallow_sticker = Sticker(rect, "marshmallow.png")
    field = PolyField(shape_schema_disambiguation)
    rect_dict = field.serialize('shape', marshmallow_sticker)

    assert rect_dict == {"length": 4, "width": 10, "color": "blue"}


def test_serializing_polyfield_None():
    rect = Rectangle(None, 4, 10)
    Sticker = namedtuple('Sticker', ['shape', 'image'])
    marshmallow_sticker = Sticker(rect, "marshmallow.png")
    field = PolyField(shape_schema_disambiguation)
    rect_dict = field.serialize('shape', marshmallow_sticker)

    assert rect_dict == {"length": 4, "width": 10, "color": None}


def test_serializing_polyfield_many():
    rect = Rectangle("blue", 4, 10)
    tri = Triangle("red", 1, 100)
    StickerCollection = namedtuple('StickerCollection', ['shapes', 'image'])
    marshmallow_sticker_collection = StickerCollection([rect, tri], "marshmallow.png")
    field = PolyField(shape_schema_disambiguation, many=True)
    shapes = field.serialize('shapes', marshmallow_sticker_collection)
    expected_shapes = [
        {"length": 4, "width": 10, "color": "blue"},
        {"base": 1, "height": 100, "color": "red"}
    ]
    assert shapes == expected_shapes


def test_invalid_polyfield():
    Sticker = namedtuple('Sticker', ['shape', 'image'])
    with pytest.raises(TypeError):
        field = PolyField(shape_schema_disambiguation)
        field.serialize('shape', Sticker(None, None))
