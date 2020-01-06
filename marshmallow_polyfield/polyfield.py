import abc
from six import raise_from, with_metaclass

from marshmallow import Schema, ValidationError
from marshmallow.fields import Field


class PolyFieldBase(with_metaclass(abc.ABCMeta, Field)):
    def __init__(self, many=False, **metadata):
        super(PolyFieldBase, self).__init__(**metadata)
        self.many = many
        self.serializer_modifies = False
        self.deserializer_modifies = False

    def _deserialize(self, value, attr, parent, **kwargs):
        if not self.many:
            value = [value]

        results = []
        for v in value:
            deserializer = None
            try:
                if self.deserializer_modifies:
                    deserializer, v = (
                        self.deserialization_modifier(v, parent)
                    )
                else:
                    deserializer = self.deserialization_schema_selector(v, parent)
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
                    if self.serializer_modifies:
                        schema, v = self.serialization_modifier(v, obj)
                    else:
                        schema = self.serialization_schema_selector(v, obj)
                    schema.context.update(getattr(self, 'context', {}))
                    res.append(schema.dump(v))
                return res
            else:
                if self.serializer_modifies:
                    schema, value = self.serialization_modifier(value, obj)
                else:
                    schema = self.serialization_schema_selector(value, obj)
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

    @abc.abstractmethod
    def serialization_modifier(self, value, obj):
        raise NotImplementedError

    @abc.abstractmethod
    def deserialization_modifier(self, value, obj):
        raise NotImplementedError


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
            serialization_modifier=None,
            deserialization_modifier=None,
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
        self._serialization_modifier_arg = serialization_modifier
        self._deserialization_modifier_arg = deserialization_modifier
        # TODO: make above exclusive to each other
        self.serializer_modifies = self._serialization_modifier_arg is not None
        self.deserializer_modifies = self._deserialization_modifier_arg is not None

    def serialization_schema_selector(self, value, obj):
        return self._serialization_schema_selector_arg(value, obj)

    def deserialization_schema_selector(self, value, obj):
        return self._deserialization_schema_selector_arg(value, obj)

    def serialization_modifier(self, value, obj):
        return self._serialization_modifier_arg(value, obj)

    def deserialization_modifier(self, value, obj):
        return self._deserialization_modifier_arg(value, obj)
