from enum import Enum


# Ship type identifier
class ShipType(Enum):
    CARRIER = 5
    BATTLESHIP = 4
    CRUISER = 3
    SUBMARINE = 2
    DESTROYER = 1
    NONE = 0
