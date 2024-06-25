import enum

@enum.unique
class ExceptionsEnum(enum.Enum):

    INVALID_ARGUMENT = (100, ValueError, "Invalid argument supplied")
    NOT_A_INTEGER = (110, ValueError, "Integer value was expected")
    NOT_A_NUMBER = (120, ValueError, "Number value was expected")
    NOT_A_FLOAT = (130, ValueError, "Floating point value was expected")
    NOT_A_SEQUENCE = (140, ValueError, "Sequence object was expected")
    NOT_A_MAPPING = (150, ValueError, "Mapping object was expected")
    ACCESS_DENIED = (200, AttributeError, "Cannot access this attribute")
    READ_ONLY_ATTRIBUTE = (210, AttributeError, "Read only attribute")
    WRITE_ONLY_ATTRIBUTE = (220, AttributeError, "Write only attribute")

    def __new__(cls, exception_code, exception_class, default_message):
        member = object.__new__(cls)
        member._value_ = exception_code
        member._exception = exception_class
        member._code = exception_code
        member._default_message = default_message
        return member

    @property
    def exception(self):
        return self._exception

    @property
    def code(self):
        return self._code

    @property
    def default_message(self):
        return self._default_message

    def throw(self, message=None, from_exception=None):
        message = self.default_message if message is None else message
        raise self.exception(self.code, message) from from_exception
