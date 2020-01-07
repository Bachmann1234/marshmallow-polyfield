import abc
from six import raise_from, with_metaclass

from marshmallow import Schema, ValidationError
from marshmallow.fields import Field, String


class PolyFieldBase(with_metaclass(abc.ABCMeta, Field)):
    def __init__(self, many=False, **metadata):
        super(PolyFieldBase, self).__init__(**metadata)
        self.many = many

    def _deserialize(self, value, attr, parent, **kwargs):
        if not self.many:
            value = [value]

        results = []
        for v in value:
            deserializer = None
            try:
                deserializer = self.deserialization_schema_selector(v, parent)
                v = self.deserialization_value_modifier(v, parent)
                if isinstance(deserializer, type):
                    deserializer = deserializer()
                if not isinstance(deserializer, (Field, Schema)):
                    raise Exception('Invalid deserializer type')
            except TypeError as te:
                raise_from(ValidationError(str(te)), te)
            except ValidationError:
                raise
            except Exception as err:
                class_type = None
                if deserializer:
                    class_type = str(type(deserializer))

                raise_from(
                    ValidationError(
                        "Unable to use schema. Error: {err}\n"
                        "Ensure there is a deserialization_schema_selector"
                        " and then it returns a field or a schema when the function is passed in "
                        "{value_passed}. This is the class I got. "
                        "Make sure it is a field or a schema: {class_type}".format(
                            err=err,
                            value_passed=v,
                            class_type=class_type
                        )
                    ),
                    err
                )

            # Will raise ValidationError if any problems
            if isinstance(deserializer, Field):
                data = deserializer.deserialize(v, attr, parent)
            else:
                deserializer.context.update(getattr(self, 'context', {}))
                data = deserializer.load(v)

            results.append(data)

        if self.many:
            return results
        else:
            # Will be at least one otherwise value would have been None
            return results[0]

    def _serialize(self, value, key, obj, **kwargs):
        if value is None:
            return None
        try:
            if self.many:
                res = []
                for v in value:
                    schema = self.serialization_schema_selector(v, obj)
                    v = self.serialization_value_modifier(v, obj)
                    schema.context.update(getattr(self, 'context', {}))
                    res.append(schema.dump(v))
                return res
            else:
                schema = self.serialization_schema_selector(value, obj)
                value = self.serialization_value_modifier(value, obj)
                schema.context.update(getattr(self, 'context', {}))
                return schema.dump(value)
        except Exception as err:
            raise TypeError(
                'Failed to serialize object. Error: {0}\n'
                ' Ensure the serialization_schema_selector exists and '
                ' returns a Schema and that schema'
                ' can serialize this value {1}'.format(err, value))

    @abc.abstractmethod
    def serialization_schema_selector(self, value, obj):
        raise NotImplementedError

    @abc.abstractmethod
    def deserialization_schema_selector(self, value, obj):
        raise NotImplementedError

    def serialization_value_modifier(self, value, obj):
        return value

    def deserialization_value_modifier(self, value, obj):
        return value


class PolyField(PolyFieldBase):
    """
    A field that (de)serializes to one of many types. Passed in functions
    are called to disambiguate what schema to use for the (de)serialization
    Intended to assist in working with fields that can contain any subclass
    of a base type
    """
    def __init__(
            self,
            serialization_schema_selector=None,
            deserialization_schema_selector=None,
            serialization_value_modifier=lambda value, obj: value,
            deserialization_value_modifier=lambda value, obj: value,
            many=False,
            **metadata
    ):
        """
        :param serialization_schema_selector: Function that takes in either
        an object representing that object, it's parent object
        and returns the appropriate schema.
        :param deserialization_schema_selector: Function that takes in either
        an a dict representing that object, dict representing it's parent dict
        and returns the appropriate schema

        """
        super(PolyField, self).__init__(many=many, **metadata)
        self._serialization_schema_selector_arg = serialization_schema_selector
        self._deserialization_schema_selector_arg = deserialization_schema_selector
        self.serialization_value_modifier = serialization_value_modifier
        self.deserialization_value_modifier = deserialization_value_modifier

    def serialization_schema_selector(self, value, obj):
        return self._serialization_schema_selector_arg(value, obj)

    def deserialization_schema_selector(self, value, obj):
        return self._deserialization_schema_selector_arg(value, obj)


def create_label_schema(schema):
    class LabelSchema(Schema):
        type = String()
        value = schema()

    return LabelSchema


class ExplicitPolyField(PolyFieldBase):
    def __init__(
            self,
            class_to_schema_mapping,
            create_label_schema=create_label_schema,
            many=False,
            **metadata
    ):
        super(ExplicitPolyField, self).__init__(many=many, **metadata)
        self._class_to_schema_mapping = class_to_schema_mapping
        self._class_to_name = {
            cls: cls.__name__
            for cls in self._class_to_schema_mapping.keys()
        }
        self._name_to_class = {
            name: cls
            for cls, name in self._class_to_name.items()
        }
        self.create_label_schema = create_label_schema

    def serialization_schema_selector(self, base_object, parent_obj):
        cls = type(base_object)
        schema = self._class_to_schema_mapping[cls]
        label_schema = self.create_label_schema(schema=schema)

        return label_schema()

    def serialization_value_modifier(self, base_object, parent_obj):
        cls = type(base_object)
        name = self._class_to_name[cls]

        return {'type': name, 'value': base_object}

    def deserialization_schema_selector(self, object_dict, parent_object_dict):
        name = object_dict['type']
        cls = self._name_to_class[name]
        schema = self._class_to_schema_mapping[cls]

        return schema()

    def deserialization_value_modifier(self, object_dict, parent_object_dict):
        return object_dict['value']
