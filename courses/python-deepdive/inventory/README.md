# Description
Class hierarchy to represent items in an inventory.

Project 3 from Python3 Deep Dive Part 4.
Inheritance kinda sucks. It produces hard-to-maintain code with hard-to-reason-about dependencies.

Project specification at [python-deepdive](https://github.com/fbaptiste/python-deepdive).

```mermaid
---
title: Conceptual Class Diagram
---
classDiagram
    direction LR
    Inventory "0..*" o-- "1" Resource
    Resource <|-- CPU
    Resource <|-- Storage
    Storage <|-- HDD
    Storage <|-- SSD
    class Resource {
        /tuple[str] components [ReadOnly]
        +int id [ReadOnly]
        +str manufacturer [ReadOnly]
        +int total
        +int allocated

        +composition() tuple[tuple[str, object]]
        +category() str
        +claim(int n) void
        +freeup(int n) void
        +remove(int n) void
        +append(int n) void
    }
    class Storage {
        +int capacity [ReadOnly]
    }
    class HDD {
        +str size [ReadOnly]
        +int rpm [ReadOnly]
    }
    class SSD {
        +str interface [ReadOnly]
    }
    class CPU {
        +int cores [ReadOnly]
        +str socket [ReadOnly]
        +int power_watts [ReadOnly]
    }
    class Inventory {
        +mappingproxy[str, tuple[Resource]] items [ReadOnly]

        +catalog() mappingproxy[str, tuple[Resource]]
        +search(**components) mappingproxy[str, tuple[Resource]]
        +append(Resource resource) void
        +remove(Resource resource) Resource
    }
```
