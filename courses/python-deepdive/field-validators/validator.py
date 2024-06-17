from abc import ABC, abstractmethod
from weakref import WeakKeyDictionary

class Validator(ABC):

    def __init__(self, store_in_descriptor=False):        
        self.store = WeakKeyDictionary() if store_in_descriptor else None

    def __set_name__(self, owner, name):
        if self.store is None and '__dict__' not in vars(owner):
            raise AttributeError(f"{owner!r} instances don't allow storage")
        self.attrname = name

    def __get__(self, obj, objtype):
        if obj is None:
            return self
        try:
            if self.store is None:
                return vars(obj)[self.attrname]
            else:
                return self.store[obj]
        except KeyError:
            raise AttributeError(
                f"{obj!r} has no attribute {self.attrname!r}") from None

    def __set__(self, obj, value):
        value = self.validate(value)
        if self.store is None:
            vars(obj)[self.attrname] = value
        else:
            self.store[obj] = value

    @abstractmethod
    def validate(self, value):
        pass

class StringValidator(Validator):

    def __init__(
            self,
            min_length=None,
            max_length=None,
            preprocessor=None,
            store_in_descriptor=False):
        super().__init__(store_in_descriptor)
        self.min_length = min_length
        self.max_length = max_length
        self.preprocessor = preprocessor

    def validate(self, value):
        if self.preprocessor is not None:
            try:
                value = self.preprocessor(value)
            except Exception:
                raise TypeError(
                    f'preprocessor broke while processing {value!r}')
        if not isinstance(value, str):
            raise TypeError(f'Expected {value!r} to be an str')
        if self.min_length is not None and len(value) < self.min_length:
            raise ValueError(
                f'Expected {value!r} to be no smaller than {self.min_length!r}')
        if self.max_length is not None and len(value) > self.max_length:
            raise ValueError(
                f'Expected {value!r} to be no bigger than {self.max_length!r}')
        return value

class NumberValidator(Validator):

    def __init__(self, minvalue=None, maxvalue=None, store_in_descriptor=False):
        super().__init__(store_in_descriptor)
        self.minvalue = minvalue
        self.maxvalue = maxvalue

    def validate(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError(f'Expected {value!r} to be an int or float')
        if self.minvalue is not None and value < self.minvalue:
            raise ValueError(
                f'Expected {value!r} to be at least {self.minvalue!r}')
        if self.maxvalue is not None and value > self.maxvalue:
            raise ValueError(
                f'Expected {value!r} to be no more than {self.maxvalue!r}')
        return value
