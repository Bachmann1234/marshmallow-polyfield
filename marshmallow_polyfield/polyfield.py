from marshmallow import ValidationError
from marshmallow.fields import Field


class PolyField(Field):
    """
    A field that (de)serializes to one of many types. a function
    is called to disambiguate what schema to use for the (de)serialization
    Intended to assist in working with fields that can contain any subclass
    of a base type
    """
    def __init__(self, disambiguation_function, many=False, **metadata):
        """
        :param disambiguation_function: Function that takes in either
        an object or a dict representing that object
        and returns the appropriate schema

        """
        super(PolyField, self).__init__(**metadata)
        self.many = many
        self.disambiguation_function = disambiguation_function

    def _deserialize(self, value):
        if not self.many:
            value = [value]

        results = []
        for v in value:
            try:
                schema = self.disambiguation_function(v)
                data, errors = schema.load(v)
            except TypeError:
                raise ValidationError(
                    "Unable to use schema. Did the disambiguation function return one?"
                )
            if errors:
                raise ValidationError(errors)
            results.append(data)

        if self.many:
            return results
        else:
            # Will be at least one otherwise value would have been None
            return results[0]

    def _serialize(self, value, key, obj):
        try:
            if self.many:
                return [self.disambiguation_function(v).dump(v).data for v in value]
            else:
                return self.disambiguation_function(value).dump(value).data
        except Exception as err:
            raise TypeError(
                'Failed to serialize object. Error: {0}\n'
                ' Ensure the selection function returns a Schema and that schema'
                ' can serialize this value {1}'.format(err, value))
