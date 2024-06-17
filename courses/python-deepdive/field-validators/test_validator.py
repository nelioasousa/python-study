import unittest
from validator import StringValidator, NumberValidator


class StringValidatorTest(unittest.TestCase):

    def test_instance_storage(self):
        class DummyClass:
            field = StringValidator()
        obj = DummyClass()
        obj.field = 'example'
        self.assertEqual(vars(obj)['field'], 'example')
    
    def test_invalid_assigments(self):
        class DummyClass:
            field = StringValidator()
        obj = DummyClass()
        for i, value in enumerate((69, 1/3, tuple(), list(), range(5))):
            with (self.subTest(subtest=i), self.assertRaises(TypeError)):
                obj.field = value

    def test_descriptor_storage(self):
        class DummyClass:
            field = StringValidator(store_in_descriptor=True)
        obj = DummyClass()
        obj.field = 'example'
        self.assertIn(obj, DummyClass.field.store)
        self.assertEqual(DummyClass.field.store.get(obj, None), 'example')
        del obj
        self.assertFalse(DummyClass.field.store)

    def test_slotted_classes(self):
        # https://github.com/python/cpython/issues/77757
        # Exceptions raised by __set_name__ are wrapped by RuntimeError
        with self.assertRaises(RuntimeError) as cm:
            class DummySlottedClass:
                __slots__ = ('field', )
                string_field = StringValidator()
        # AttributeError expected from __set_name__
        self.assertIsInstance(cm.exception.__cause__, AttributeError)

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
        with self.subTest(subtest='string_preprocessing'):
            class DummyClass:
                field = StringValidator(preprocessor=(lambda s: s.lower()))
            obj = DummyClass()
            obj.field = 'HeLLo'
            self.assertEqual(obj.field, 'hello')
        with self.subTest(subtest='conversion_to_string'):
            class AnotherDummy:
                field = StringValidator(preprocessor=(lambda v: str(v)))
            obj = AnotherDummy()
            obj.field = 69
            self.assertEqual(obj.field, str(69))
            obj.field = [1, 2, 3]
            self.assertEqual(obj.field, str([1, 2, 3]))

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

    def test_descriptor_storage(self):
        class DummyClass:
            field = NumberValidator(store_in_descriptor=True)
        obj = DummyClass()
        obj.field = 9999.9
        self.assertIn(obj, DummyClass.field.store)
        self.assertEqual(DummyClass.field.store.get(obj, None), 9999.9)
        del obj
        self.assertFalse(DummyClass.field.store)

    def test_invalid_assigments(self):
        class DummyClass:
            field = NumberValidator()
        obj = DummyClass()
        for i, value in enumerate(('hi', tuple(), list(), range(5))):
            with (self.subTest(subtest=i), self.assertRaises(TypeError)):
                obj.field = value

    def test_slotted_classes(self):
        # https://github.com/python/cpython/issues/77757
        # Exceptions raised by __set_name__ are wrapped by RuntimeError
        with self.assertRaises(RuntimeError) as cm:
            class DummySlottedClass:
                __slots__ = ('field', )
                number_field = NumberValidator()
        # AttributeError expected from __set_name__
        self.assertIsInstance(cm.exception.__cause__, AttributeError)

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
