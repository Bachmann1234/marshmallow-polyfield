from marshmallow_polyfield.polyfield import PolyFieldBase


class TrivialExample(PolyFieldBase):
    def serialization_schema_selector(self, value, obj):
        super(TrivialExample, self).serialization_schema_selector(value, obj)

    def deserialization_schema_selector(self, value, obj):
        super(TrivialExample, self).deserialization_schema_selector(value, obj)


def test_polyfield_base():
    te = TrivialExample()
    try:
        te.serialization_schema_selector(None, None)
    except NotImplementedError:
        pass
    else:
        assert False, 'expected to raise'

    try:
        te.deserialization_schema_selector(None, None)
    except NotImplementedError:
        pass
    else:
        assert False, 'expected to raise'
