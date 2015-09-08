# -*- coding: utf-8 -*-
from marshmallow import Schema, fields


class Shape(object):
    def __init__(self, color):
        self.color = color

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class ShapeSchema(Schema):
    color = fields.Str(allow_none=True)


class Triangle(Shape):
    def __init__(self, color, base, height):
        super(Triangle, self).__init__(color)
        self.base = base
        self.height = height


class TriangleSchema(ShapeSchema):
    base = fields.Int(required=True)
    height = fields.Int(required=True)

    def make_object(self, data):
        return Triangle(
            color=data['color'],
            base=data['base'],
            height=data['height']
        )


class Rectangle(Shape):
    def __init__(self, color, length, width):
        super(Rectangle, self).__init__(color)
        self.length = length
        self.width = width


class RectangleSchema(ShapeSchema):
    length = fields.Int(required=True)
    width = fields.Int(required=True)

    def make_object(self, data):
        return Rectangle(
            color=data['color'],
            length=data['length'],
            width=data['width']
        )


def shape_schema_serialization_disambiguation(base_object):
    class_to_schema = {
        Rectangle.__name__: RectangleSchema,
        Triangle.__name__: TriangleSchema
    }
    try:
        return class_to_schema[base_object.__class__.__name__]()
    except KeyError:
        pass

    raise TypeError("Could not detect type. "
                    "Did not have a base or a length. "
                    "Are you sure this is a shape?")


def shape_schema_deserialization_disambiguation(object_dict):
    if object_dict.get("base"):
        return TriangleSchema()
    elif object_dict.get("length"):
        return RectangleSchema()

    raise TypeError("Could not detect type. "
                    "Did not have a base or a length. "
                    "Are you sure this is a shape?")
