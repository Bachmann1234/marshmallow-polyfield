from unittest import TestCase

from marshmallow_polyfield.polyfield import PolyFieldBase


class TestPolyFieldBase(TestCase):
    def run_test(self):
        with self.assertRaises(NotImplementedError):
            PolyFieldBase.serialization_schema_selector(None, None, None)

        with self.assertRaises(NotImplementedError):
            PolyFieldBase.deserialization_schema_selector(None, None, None)
