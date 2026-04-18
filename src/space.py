from math import floor
from dataclasses import dataclass


ASPECT = 1.3 # height:width
DOT_WIDTH = 2
DOT_HEIGHT = 4


@dataclass
class Space:
    x: float
    y: float


    @classmethod
    def relative(cls, x: float, y: float, size: tuple[int, int]) -> Space:
        x, y = x * size[0], y * size[1]
        return cls(x, y)


    @property
    def cell(self) -> tuple[int, int]:
        return int(floor(self.x)), int(floor(self.y))


@dataclass
class WorldSpace(Space):
    @property
    def disp(self) -> DisplaySpace:
        x, y = self.x, self.y / ASPECT
        return DisplaySpace(x, y)


    @property
    def dot(self) -> DotSpace:
        x, y = self.x * DOT_WIDTH, (self.y * DOT_HEIGHT) / ASPECT
        return DotSpace(x, y)


@dataclass
class DisplaySpace(Space):
    @property
    def world(self) -> WorldSpace:
        x, y = self.x, self.y * ASPECT
        return WorldSpace(x, y)


    @property
    def dot(self) -> DotSpace:
        x, y = self.x * DOT_WIDTH, self.y * DOT_HEIGHT
        return DotSpace(x, y)


@dataclass
class DotSpace(Space):
    @property
    def bit(self) -> int:
        x, y = self.cell
        x, y = x % DOT_WIDTH, y % DOT_HEIGHT
        return (3 * x) + y if y < 3 else x + 6


    @property
    def world(self) -> WorldSpace:
        x, y = self.x / DOT_WIDTH, (self.y / DOT_HEIGHT) * ASPECT
        return WorldSpace(x, y)


    @property
    def disp(self) -> DisplaySpace:
        x, y = self.x / DOT_WIDTH, self.y / DOT_HEIGHT
        return DisplaySpace(x, y)
