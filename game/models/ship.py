from dataclasses import dataclass, field

from .ship_type import ShipType

# Actual cell counts per ship type.
# NOTE: ShipType enum values are priority IDs, not sizes.
# SUBMARINE.value=2 but size=3; PATROL_BOAT.value=1 but size=2.
_SHIP_SIZES: dict[ShipType, int] = {
    ShipType.CARRIER: 5,
    ShipType.BATTLESHIP: 4,
    ShipType.DESTROYER: 3,
    ShipType.SUBMARINE: 3,
    ShipType.PATROL_BOAT: 2,
}


def get_ship_size(ship_type: ShipType) -> int:
    return _SHIP_SIZES[ship_type]


def get_ship_name(ship_type: ShipType) -> str:
    display = "Patrol Boat" if ship_type is ShipType.PATROL_BOAT else ship_type.name.capitalize()
    return f"{display} ({get_ship_size(ship_type)})"


@dataclass
class Ship:
    ship_type: ShipType
    valid_ships = list(_SHIP_SIZES.keys())

    # NOTE: dicts are ordered in Python 3.7+, _SHIP_SIZES.keys() is consistent
    @staticmethod
    def get_fleet() -> list[ShipType]:
        return Ship.valid_ships

    # Zero-indexed (row, col) pairs occupied by this ship.
    cells: list[tuple[int, int]]
    hits: int = field(default=0, init=False)

    @property
    def size(self) -> int:
        return get_ship_size(self.ship_type)

    @property
    def is_sunk(self) -> bool:
        return self.hits >= self.size

    def register_hit(self) -> None:
        self.hits += 1

    def __repr__(self) -> str:
        return f"Ship(type={self.ship_type}, cells={self.cells}, hits={self.hits})"
