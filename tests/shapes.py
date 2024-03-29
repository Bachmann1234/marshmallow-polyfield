from marshmallow import Schema, fields, post_load, ValidationError


class Shape(object):
    def __init__(self, color):
        self.color = color

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class ShapeSchema(Schema):
    color = fields.Str(allow_none=True)

    @post_load
    def make_object(self, data, **_):
        return Shape(**data)


class Triangle(Shape):
    def __init__(self, color, base, height):
        super().__init__(color)
        self.base = base
        self.height = height


class TriangleSchema(ShapeSchema):
    base = fields.Int(required=True)
    height = fields.Int(required=True)

    @post_load
    def make_object(self, data, **_):
        return Triangle(
            color=data['color'],
            base=data['base'],
            height=data['height']
        )


class Rectangle(Shape):
    def __init__(self, color, length, width):
        super().__init__(color)
        self.length = length
        self.width = width


class RectangleSchema(ShapeSchema):
    length = fields.Int(required=True)
    width = fields.Int(required=True)

    @post_load
    def make_object(self, data, **_):
        return Rectangle(
            color=data['color'],
            length=data['length'],
            width=data['width']
        )


def shape_schema_serialization_disambiguation(base_object, _):
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


def shape_property_schema_serialization_disambiguation(base_object, obj):
    type_to_schema = {
        'rectangle': RectangleSchema,
        'triangle': TriangleSchema
    }
    try:
        return type_to_schema[obj.type]()
    except KeyError:
        pass

    raise TypeError("Could not detect type. "
                    "Did not have a base or a length. "
                    "Are you sure this is a shape?")


def shape_schema_deserialization_disambiguation(object_dict, _):
    if object_dict.get("base"):
        if object_dict.get("base") < 0:
            raise ValidationError("Base cannot be negative.")
        return TriangleSchema()
    elif object_dict.get("length"):
        if object_dict.get("length") < 0:
            raise Exception("Bad Case")
        return RectangleSchema()

    raise TypeError("Could not detect type. "
                    "Did not have a base or a length. "
                    "Are you sure this is a shape?")


def shape_property_schema_deserialization_disambiguation(object_dict, data):
    type_to_schema = {
        'rectangle': RectangleSchema,
        'triangle': TriangleSchema
    }

    try:
        return type_to_schema[data['type']]()
    except KeyError:
        pass

    raise TypeError("Could not detect type. "
                    "Did not have a base or a length. "
                    "Are you sure this is a shape?")


def fuzzy_schema_deserialization_disambiguation(data, _):
    if isinstance(data, dict):
        return ShapeSchema
    if isinstance(data, str):
        return fields.Email

    raise TypeError('Could not detect type. '
                    'Are you sure this is a shape or an email?')


def fuzzy_pos_schema_selector(data, _):
    if isinstance(data, str):
        return fields.Email
    if isinstance(data, dict):
        return fields.Dict(keys=fields.Str, values=fields.Dict(values=fields.Int))

    raise TypeError('Could not detect type. '
                    'Are you sure this is a positions or an email?')


def fuzzy_pos_schema_selector_by_type(_, parent):
    type_str = parent.get('type')
    if type_str == 'str':
        return fields.Email
    elif type_str == 'dict':
        return fields.Dict(keys=fields.Str, values=fields.Dict(values=fields.Int))

    raise TypeError('Could not detect type. '
                    'Are you sure that "type" value in ("str", "dict")?')
