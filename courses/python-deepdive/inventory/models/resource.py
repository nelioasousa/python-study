class Resource:
    _composition = ("id", "manufacturer")

    def __init__(self, id, manufacturer):
        id = int(id)
        self._raise_if_negative(id, "'id' must be a non-negative integer")
        self._id = id
        self._manufacturer = str(manufacturer)
        self.allocated = 0
        self.total = 0

    @classmethod
    def category(cls):
        return cls.__name__.lower()

    @classmethod
    def composition(cls):
        return cls._composition

    @staticmethod
    def _raise_if_negative(number, message=None):
        if number < 0:
            raise ValueError(
                "Negative integer not allowed" if message is None else message
            )

    @property
    def id(self):
        return self._id

    @property
    def manufacturer(self):
        return self._manufacturer

    @property
    def components(self):
        return tuple((attr, getattr(self, attr)) for attr in self.composition())

    @property
    def total(self):
        try:
            return self._total
        except AttributeError:
            self._total = 0
            return self._total

    @total.setter
    def total(self, value):
        value = int(value)
        self._raise_if_negative(value)
        if value < self.allocated:
            raise ValueError("'total' can't be smaller than 'allocated'")
        self._total = value

    @property
    def allocated(self):
        try:
            return self._allocated
        except AttributeError:
            self._allocated = 0
            return self._allocated

    @allocated.setter
    def allocated(self, value):
        value = int(value)
        self._raise_if_negative(value)
        if value > self.total:
            raise ValueError("'allocated' can't be larger than 'total'")
        self._allocated = value

    def __repr__(self):
        return str(self)
    
    def __str__(self):
        return "%s(%s)" %(
            type(self).__name__,
            ", ".join(
                f"{attr}={getattr(self, attr)}" for attr in self.composition()
            )
        )
    
    def __eq__(self, other):
        if isinstance(other, dict):
            for attr in self.composition():
                try:
                    if getattr(self, attr) != other[attr]:
                        return False
                except KeyError:
                    return False        
            return True
        if not isinstance(other, type(self)):
            return NotImplemented
        if frozenset(self.composition()) != frozenset(other.composition()):
            return False
        for attr in self.composition():
            if getattr(self, attr) != getattr(other, attr):
                return False
        return True

    def has(self, **components):
        for attr, value in components.items():
            try:
                if getattr(self, attr) != value:
                    return False
            except AttributeError:
                return False
        return True

    def claim(self, n, /):
        n = int(n)
        self._raise_if_negative(n)
        if n > (self.total - self.allocated):
            raise ValueError("Not enough resources")
        self.allocated += n

    def freeup(self, n, /):
        n = int(n)
        self._raise_if_negative(n)
        if n > self.allocated:
            raise ValueError("Trying to free more than allocated")
        self.allocated -= n

    def remove(self, n, /):
        n = int(n)
        self._raise_if_negative(n)
        if n > (self.total - self.allocated):
            raise ValueError("Trying to remove more than available")
        self.total -= n
    
    def append(self, n, /):
        n = int(n)
        self._raise_if_negative(n)
        self.total += n
