# mashmallow-polyfield

[![Documentation Status](https://readthedocs.org/projects/marshmallow-polyfield/badge/?version=latest)](https://readthedocs.org/projects/marshmallow-polyfield/?badge=latest)
[![Build](https://travis-ci.org/Bachmann1234/marshmallow-polyfield.svg?branch=master)](https://travis-ci.org/Bachmann1234/marshmallow-polyfield.svg?branch=master)
[![Coverage Status](https://coveralls.io/repos/Bachmann1234/marshmallow-polyfield/badge.svg?branch=master&service=github)](https://coveralls.io/github/Bachmann1234/marshmallow-polyfield?branch=master)


An extension to marshmallow to allow for polymorphic fields

Marshmallow is a fantastic library for serialization and deserialization of data. 
For more on that project see its [GitHub](https://github.com/marshmallow-code/marshmallow) page or its [Documentation](http://marshmallow.readthedocs.org/en/latest/)

This project adds a custom field designed for polymorphic types. This allows you to define a schema that says "This field accepts anything of type X"

The secret to this field is that you need to define a function that the field can use to deterime what Marshmallow Schema to use for 
serialization and deserialization. 

An example can be seen in `tests/shapes.py` in `shape_schema_disambiguation` 

This function takes in one value which can either be a dictionary in the case of deserialization or an object in the case of serialization.

This function must inspect the object and return the appropriate Schema or raise a `TypeError` if one cannot be found

This field should support the same properties as other Marshmallow fields. I have worked with `required` `allow_none` and `many`.

Below is an example schema using this field.


```
def shape_schema_disambiguation(value):
    class_to_schema = {
        Rectangle.__name__: RectangleSchema,
        Triangle.__name__: TriangleSchema
    }
    try:
        return class_to_schema[value.__class__.__name__]()
    except KeyError:
        pass

    try:
        if value.get("base"):
            return TriangleSchema()
        elif value.get("length"):
            return RectangleSchema()
    except AttributeError:
        pass

    raise TypeError("Could not detect type. "
                    "Did not have a base or a length. "
                    "Are you sure this is a shape?")
                    
class ContrivedShapeClass(object):
    def __init__(self, main, others):
        self.main = main
        self.others = others

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

class ContrivedShapeClassSchema(Schema):
    main = PolyField(shape_schema_disambiguation, required=True)
    others = PolyField(shape_schema_disambiguation, allow_none=True, many=True)

    def make_object(self, data):
        return TestPolyField.ContrivedShapeClass(
            data.get('main'),
            data.get('others')
        )
```