import re

from marshmallow import fields
from marshmallow_polyfield.polyfield import (
    ExplicitPolyField,
    ExplicitNamesNotUniqueError,
    PolyFieldBase,
)
import pytest


class TrivialExample(PolyFieldBase):
    def serialization_schema_selector(self, value, obj):
        super().serialization_schema_selector(value, obj)

    def deserialization_schema_selector(self, value, obj):
        super().deserialization_schema_selector(value, obj)


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


def test_explicit_polyfield_raises_for_nonunique_names():
    same_name = 'same name'

    with pytest.raises(
            ExplicitNamesNotUniqueError,
            match=re.escape("{'same name': [<class 'int'>, <class 'str'>]}"),
    ):
        ExplicitPolyField(
            class_to_schema_mapping={
                str: fields.String,
                int: fields.Integer,
            },
            class_to_name_overrides={str: same_name, int: same_name},
        )
