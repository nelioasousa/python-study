import unittest
from validator import StringValidator, NumberValidator


class StringValidatorTest(unittest.TestCase):

    def test_instance_storage(self):
        class DummyClass:
            field = StringValidator()
        obj = DummyClass()
        obj.field = 'example'
        self.assertEqual(vars(obj)['field'], 'example')
        with self.assertRaises(TypeError):
            obj.field = 69

    def test_descriptor_storage(self):
        class DummyClass:
            field = StringValidator(store_in_descriptor=True)
        obj = DummyClass()
        obj.field = 'example'
        self.assertIn(obj, DummyClass.field.store)
        self.assertEqual(DummyClass.field.store.get(obj, None), 'example')
        with self.assertRaises(TypeError):
            obj.field = 69
        del obj
        self.assertFalse(DummyClass.field.store)

    def test_slotted_classes(self):
        # https://github.com/python/cpython/issues/77757
        # Exceptions raised by __set_name__ are wrapped by RuntimeError
        try:
            class DummySlottedClass:
                __slots__ = ('field', )
                string_field = StringValidator()
        # AttributeError expected from __set_name__
        except RuntimeError as e:
            self.assertIsInstance(e.__cause__, AttributeError)

    def test_length_contraints(self):
        class DummyClass:
            field = StringValidator(5, 7)
        obj = DummyClass()
        with self.assertRaises(ValueError):
            obj.field = '1234'
        obj.field = '12345'
        self.assertEqual(obj.field, '12345')
        obj.field = '1234567'
        self.assertEqual(obj.field, '1234567')
        with self.assertRaises(ValueError):
            obj.field = '12345678'

    def test_preprocessor(self):
        class DummyClass:
            field = StringValidator(preprocessor=(lambda s: s.lower()))
        obj = DummyClass()
        obj.field = 'HeLLo'
        self.assertEqual(obj.field, 'hello')

    def test_preprocessor_and_length_contraints(self):
        class DummyClass:
            field = StringValidator(
                min_length=3, max_length=5, preprocessor=(lambda s: s.strip()))
        obj = DummyClass()
        obj.field = ' 123 '
        self.assertEqual(obj.field, '123')
        with self.assertRaises(ValueError):
            obj.field = '  1  '
        obj.field = ' 12345 '
        self.assertEqual(obj.field, '12345')


class NumberValidatorTest(unittest.TestCase):

    def test_instance_storage(self):
        class DummyClass:
            field = NumberValidator()
        obj = DummyClass()
        obj.field = 5000
        self.assertEqual(vars(obj)['field'], 5000)
        with self.assertRaises(TypeError):
            obj.field = 'hi'

    def test_descriptor_storage(self):
        class DummyClass:
            field = NumberValidator(store_in_descriptor=True)
        obj = DummyClass()
        obj.field = 9999.5
        self.assertIn(obj, DummyClass.field.store)
        self.assertEqual(DummyClass.field.store.get(obj, None), 9999.5)
        with self.assertRaises(TypeError):
            obj.field = [9, 9, 9, 9, 0.5]
        del obj
        self.assertFalse(DummyClass.field.store)

    def test_slotted_classes(self):
        # https://github.com/python/cpython/issues/77757
        # Exceptions raised by __set_name__ are wrapped by RuntimeError
        try:
            class DummySlottedClass:
                __slots__ = ('field', )
                number_field = NumberValidator()
        # AttributeError expected from __set_name__
        except RuntimeError as e:
            self.assertIsInstance(e.__cause__, AttributeError)

    def test_size_contraints(self):
        class DummyClass:
            field = NumberValidator(50, 100.0)
        obj = DummyClass()
        for number in (-50.0, -20, 0, 100.1, 500):
            with self.assertRaises(ValueError):
                obj.field = number
        obj.field = 51
        self.assertEqual(obj.field, 51)
        obj.field = 90.0
        self.assertEqual(obj.field, 90.0)


if __name__ == '__main__':
    unittest.main()
