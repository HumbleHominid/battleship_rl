from enum import Enum


# Ship type identifier
class ShipType(Enum):
    CARRIER = 5
    BATTLESHIP = 4
    DESTROYER = 3
    SUBMARINE = 2
    PATROL_BOAT = 1
    NONE = 0
