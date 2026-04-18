from typing import Generic, TypeVar
from src.space import DisplayBounds


T = TypeVar('T', bound=object)


class Cell(Generic[T]):
    meta: T
    val: str


    def __init__(self, val: str = ' ') -> None:
        self.val = val


    def __or__(self, other: Cell[T]) -> Cell[T]:
        if other.val == ' ':
            return self
        return other


    def __ior__(self, other: Cell[T]) -> Cell[T]:
        if other.val == ' ':
            self.meta = other.meta
            self.val = other.val
        return self


    def attach(self, meta: T) -> None:
        self.meta = meta


class Display(Generic[T]):
    cells: list[list[Cell[T]]]
    bounds: DisplayBounds


    def __init__(self, bounds: DisplayBounds) -> None:
        self.cells = [[Cell[T]() for _ in range(bounds.w)] for _ in range(bounds.h)]
        self.bounds = bounds


    def __getitem__(self, key: int | tuple[int, int]) -> list[Cell[T]] | Cell[T]:
        if isinstance(key, int):
            y = key
            return self.cells[y]
        if isinstance(key, tuple):
            x, y = key
            return self.cells[y][x]


    def __setitem__(self, key: tuple[int, int], val: Cell[T]) -> None:
        x, y = key
        self.cells[y][x] = val


    def __or__(self, other: Display[T]) -> Display[T]:
        bounds = DisplayBounds(max(self.bounds.w, other.bounds.w), max(self.bounds.h, other.bounds.h))
        result = Display[T](bounds)

        d0, d1 = self.cells, other.cells
        for y, (l0, l1) in enumerate(zip(d0, d1)):
            for x, (c0, c1) in enumerate(zip(l0, l1)):
                result[x, y] = c0 | c1

        return result


    def __ior__(self, other: Display[T]) -> Display[T]:
        bounds = DisplayBounds(max(self.bounds.w, other.bounds.w), max(self.bounds.h, other.bounds.h))
        result = Display[T](bounds)

        d0, d1 = self.cells, other.cells
        for y, (l0, l1) in enumerate(zip(d0, d1)):
            for x, (c0, c1) in enumerate(zip(l0, l1)):
                result[x, y] = c0 | c1

        self.cells = result.cells
        self.bounds = bounds
        return self
