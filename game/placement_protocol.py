from typing import Protocol, runtime_checkable

from .models import Ship, ShipType


@runtime_checkable
class PlacementTarget(Protocol):
    def can_place_ship(
        self, ship_type: ShipType, row: int, col: int, direction: str
    ) -> tuple[bool, str]: ...

    def place_ship(
        self, ship_type: ShipType, row: int, col: int, direction: str
    ) -> Ship: ...

    def get_placed_cells(self) -> list[tuple[int, int]]: ...
