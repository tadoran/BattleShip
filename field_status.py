from enum import Enum


class FieldStatus(Enum):
    EMPTY = ""
    SHIP_FIXED = 1
    SHIP_DESTROYED = "*"
    SHOT = "x"
    OCCUPIED = 5


class ShipStatus(Enum):
    FIXED = 0
    DAMAGED = 1
    DESTROYED = 2


class ShipClass(Enum):
    Battleship = 4
    Cruiser = 3
    Destroyer = 2
    Submarine = 1
