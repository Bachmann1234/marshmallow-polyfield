import abc
from six import with_metaclass

from marshmallow import ValidationError
from marshmallow.fields import Field


class PolyFieldBase(with_metaclass(abc.ABCMeta, Field)):
    def __init__(self, many=False, **metadata):
        super(PolyFieldBase, self).__init__(**metadata)
        self.many = many

    def _deserialize(self, value, attr, data):
        if not self.many:
            value = [value]

        results = []
        for v in value:
            schema = None
            try:
                schema = self.deserialization_schema_selector(v, data)
                assert hasattr(schema, 'load')
            except Exception:
                schema_message = None
                if schema:
                    schema_message = str(type(schema))

                raise ValidationError(
                    "Unable to use schema. Ensure there is a deserialization_schema_selector"
                    " and that it returns a schema when the function is passed in {value_passed}."
                    " This is the class I got. Make sure it is a schema: {class_type}".format(
                        value_passed=v,
                        class_type=schema_message
                    )
                )
            schema.context.update(getattr(self, 'context', {}))
            # Will raise ValidationError if any problems
            data = schema.load(v)
            results.append(data)

        if self.many:
            return results
        else:
            # Will be at least one otherwise value would have been None
            return results[0]

    def _serialize(self, value, key, obj):
        if value is None:
            return None
        try:
            if self.many:
                res = []
                for v in value:
                    schema = self.serialization_schema_selector(v, obj)
                    schema.context.update(getattr(self, 'context', {}))
                    res.append(schema.dump(v))
                return res
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

    def serialization_schema_selector(self, value, obj):
        return self._serialization_schema_selector_arg(value, obj)

    def deserialization_schema_selector(self, value, obj):
        return self._deserialization_schema_selector_arg(value, obj)
