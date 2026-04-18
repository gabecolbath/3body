from typing import Generic, TypeVar


DEFAULT_CHAR = ' '
DEFAULT_COLOR = "#ffffff"


T = TypeVar('T', bound=object)


class Pixel(Generic[T]):
    char: str
    color: str
    meta: T


    def __init__(self, char: str = DEFAULT_CHAR, color: str = DEFAULT_COLOR) -> None:
        self.char = char
        self.color = color


    def __or__(self, other: Pixel) -> Pixel:
        if not other.char == ' ':
            return other
        return self


    def __ior__(self, other: Pixel) -> Pixel:
        self = self | other
        return self


    def attach(self, meta: T) -> None:
        self.meta = meta


    def clear(self) -> None:
        self.char = DEFAULT_CHAR
        self.color = DEFAULT_COLOR


class Line(Generic[T]):
    pixels: list[Pixel[T]]


    def __init__(self, size: int = 0) -> None:
        self.pixels = [Pixel() for _ in range(size)]


    def __setitem__(self, key: int, val: Pixel) -> None:
        self.pixels[key] = val


    def __getitem__(self, key: int) -> Pixel:
        return self.pixels[key]


    def __len__(self) -> int:
        return len(self.pixels)


    def __or__(self, other: Line) -> Line:
        size = max(len(self), len(other))
        line = Line(size)
        for i, (px0, px1) in enumerate(zip(self.pixels, other.pixels)):
            line[i] = px0 | px1
        return line


    def __ior__(self, other: Line) -> Line:
        self = self | other
        return self


    def resize(self, size: int) -> None:
        line = Line(size)
        copy = min(len(self), size)
        for x in range(copy):
            line[x] = self[x]
        self.pixels = line.pixels


    def clear(self) -> None:
        for px in self.pixels:
            px.clear()


class Display(Generic[T]):
    lines: list[Line[T]]
    size: tuple[int, int]


    def __init__(self, size: tuple[int, int] = (0, 0)) -> None:
        self.lines = [Line(size[1]) for _ in range(size[0])]
        self.size = size


    def __setitem__(self, key: int, val: Line) -> None:
        self.lines[key] = val


    def __getitem__(self, key: int) -> Line:
        return self.lines[key]


    def __len__(self) -> int:
        return len(self.lines)


    def __or__(self, other: Display) -> Display:
        size = (max(self.size[0], other.size[0]), max(self.size[1], other.size[1]))
        disp = Display(size)
        for i, (l0, l1) in enumerate(zip(self.lines, other.lines)):
            disp[i] = l0 | l1
        return disp


    def __ior__(self, other: Display) -> Display:
        self = self | other
        return self


    def resize(self, size: tuple[int, int]) -> None:
        disp = Display(size)
        copy = (min(self.size[0], size[0]), min(self.size[1], size[1]))
        for y in range(copy[0]):
            for x in range(copy[1]):
                disp[y][x] = self[y][x]
        self.lines = disp.lines
        self.size = size


    def clear(self) -> None:
        for line in self.lines:
            line.clear()
