import unittest
from exceptions import ExceptionsEnum

class ExceptionsEnumTest(unittest.TestCase):

    def test_invalid_argument(self):
        with self.assertRaises(ValueError) as cm:
            ExceptionsEnum.INVALID_ARGUMENT.throw()
        self.assertEqual(cm.exception.args[0],
                         ExceptionsEnum.INVALID_ARGUMENT.code)
        self.assertEqual(cm.exception.args[1],
                         ExceptionsEnum.INVALID_ARGUMENT.default_message)
    
    def test_access_denied(self):
        with self.assertRaises(AttributeError) as cm:
            ExceptionsEnum.ACCESS_DENIED.throw()
        self.assertEqual(cm.exception.args[0],
                         ExceptionsEnum.ACCESS_DENIED.code)
        self.assertEqual(cm.exception.args[1],
                         ExceptionsEnum.ACCESS_DENIED.default_message)

if __name__ == '__main__':
    unittest.main()
