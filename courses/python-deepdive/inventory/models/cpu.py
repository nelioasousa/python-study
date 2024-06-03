from resource import Resource


class CPU(Resource):
    _composition = ("id", "manufacturer", "cores", "socket", "power_watts")

    def __init__(self, id, manufacturer, cores, socket, power_watts):
        super().__init__(id, manufacturer)
        cores = int(cores)
        if cores < 1:
            raise ValueError("'cores' must be a positive integer")
        self._cores = cores
        self._socket = str(socket)
        power_watts = int(power_watts)
        if power_watts < 1:
            raise ValueError("'power_watts' must be a positive integer")
        self._power_watts = power_watts
    
    @property
    def cores(self):
        return self._cores
    
    @property
    def socket(self):
        return self._socket
    
    @property
    def power_watts(self):
        return self._power_watts
