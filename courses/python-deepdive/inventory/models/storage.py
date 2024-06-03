from resource import Resource


class Storage(Resource):
    _composition = ("id", "manufacturer", "capacity")

    def __init__(self, id, manufacturer, capacity):
        super().__init__(id, manufacturer)
        capacity = int(capacity)
        if capacity < 1:
            raise ValueError("'capacity' must be a positive integer")
        self._capacity = capacity
    
    @property
    def capacity(self):
        return self._capacity


class HDD(Storage):
    _composition = ("id", "manufacturer", "capacity", "size", "rpm")

    def __init__(self, id, manufacturer, capacity, size, rpm):
        super().__init__(id, manufacturer, capacity)
        self._size = str(size)
        rpm = int(rpm)
        if rpm < 1:
            raise ValueError("'rpm' must be a positive integer")
        self._rpm = rpm
    
    @property
    def size(self):
        return self._size
    
    @property
    def rpm(self):
        return self._rpm


class SSD(Storage):
    _composition = ("id", "manufacturer", "capacity", "interface")

    def __init__(self, id, manufacturer, capacity, interface):
        super().__init__(id, manufacturer, capacity)
        self._interface = str(interface)
    
    @property
    def interface(self):
        return self._interface
