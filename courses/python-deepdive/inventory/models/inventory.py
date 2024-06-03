from types import MappingProxyType
from resource import *
from storage import *
from cpu import *


class Inventory:
    def __init__(self):
        self._items = dict()

    @property
    def items(self):
        return MappingProxyType({k: tuple(v) for k, v in self._items.items()})

    def catalog(self):
        return self.items

    def search(self, **components):
        return MappingProxyType({
            ctg: tuple(rsc for rsc in items if rsc.has(**components))
            for ctg, items in self._items.items()
        })

    def append(self, resource):
        self._items.setdefault(resource.category(), list()).append(resource)

    def remove(self, resource):
        try:
            ctg_items = self._items[resource.category()]
        except KeyError:
            return None
        for i, r in enumerate(ctg_items):
            if r == resource:
                removed = ctg_items.pop(i)
                if not ctg_items:
                    self._items.pop(resource.category())
                return removed
        return None
