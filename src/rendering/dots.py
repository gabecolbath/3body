import math
import numpy as np
import numpy.typing as npt

from src.rendering.display import Pixel, Line, Display


ASPECT = 1.3
PIXEL_SIZE = (4, 2)


class Dots:
    pixels: npt.NDArray[np.uint8]
    dirtys: npt.NDArray[np.uint8]
    colors: npt.NDArray[np.uint32]
    size: tuple[int, int]


    @staticmethod
    def world_to_dot(y: float, x: float) -> tuple[int, int]:
        return int(math.floor(y * PIXEL_SIZE[0])), int(math.floor(x * PIXEL_SIZE[1]))


    @staticmethod
    def world_to_pixel(y: float, x: float) -> tuple[int, int]:
        return int(math.floor(y)), int(math.floor(x))


    @staticmethod
    def pixel_to_dot(y: int, x: int) -> tuple[int, int]:
        return y * PIXEL_SIZE[0], x * PIXEL_SIZE[1]


    @property
    def dot_size(self) -> tuple[int, int]:
        return (self.size[0] * PIXEL_SIZE[0], self.size[1] * PIXEL_SIZE[1])


    def __init__(self, size: tuple[int, int] = (0, 0)) -> None:
        self.size = size
        self.pixels = np.zeros(size, dtype=np.uint8)
        self.dirtys = np.zeros(size[0], dtype=np.uint8)
        self.colors = np.full(self.dot_size, 0xffffff, dtype=np.uint32)


    def char(self, y: int, x: int) -> str:
        code = int(self.pixels[y, x] & 0xff)
        return chr(0x2800 | code) if code != 0 else ' '


    def pixel(self, y: int, x: int) -> Pixel:
        dot_map = self.dot_map(y, x).flatten()
        color_map = self.color_map(y, x).flatten()

        colors = color_map[np.where(dot_map)[0]]
        color = int(np.sum(colors) // len(colors))
        return Pixel(self.char(y, x), f"#{color:06x}")


    def line(self, y: int) -> Line:
        line = Line(self.size[1])
        if self.dirtys[y] == 0:
            return line
        for x in range(self.size[1]):
            line[x] = self.pixel(y, x)
        return line


    def display(self) -> Display:
        disp = Display(self.size)
        for y in range(self.size[0]):
            disp[y] = self.line(y)
        return disp


    def inbounds(self, y: int, x: int) -> bool:
        by, bx = self.size
        return (0 <= y < by) and (0 <= x < bx)


    def dot_inbounds(self, y: int, x: int) -> bool:
        by, bx = self.dot_size
        return (0 <= y < by) and (0 <= x < bx)


    def dot_map(self, y: int, x: int) -> np.ndarray:
        dots = self.pixels[y, x] & 0xff
        d00 = (dots >> 0) & 1
        d10 = (dots >> 1) & 1
        d20 = (dots >> 2) & 1
        d30 = (dots >> 6) & 1
        d01 = (dots >> 3) & 1
        d11 = (dots >> 4) & 1
        d21 = (dots >> 5) & 1
        d31 = (dots >> 7) & 1
        mapped = np.array([
            [d00, d01],
            [d10, d11],
            [d20, d21],
            [d30, d31],
        ], dtype=np.uint8)
        return mapped


    def color_map(self, y: int, x: int) -> np.ndarray:
        dy, dx = Dots.pixel_to_dot(y, x)
        colors = self.colors[dy:(dy + PIXEL_SIZE[0]), dx:(dx + PIXEL_SIZE[1])]
        return colors


    def set(self, y: int, x: int, val: int) -> None:
        if not self.inbounds(y, x):
            return
        self.pixels[y, x] = (val & 0xff)
        self.dirtys[y] = 1


    def dot_set(self, y: int, x: int, val: int, color: str | None = None) -> None:
        if not self.dot_inbounds(y, x):
            return

        py, px = y // PIXEL_SIZE[0], x // PIXEL_SIZE[1]
        dy, dx = y % PIXEL_SIZE[0], x % PIXEL_SIZE[1]
        i, d = (dx * 3) + dy if (dy < 3) else dx + 6, 1 & val
        c, s = ~(1 << i) & 0xff, (d << i) & 0xff

        self.pixels[py, px] &= c
        self.pixels[py, px] |= s
        self.dirtys[py] = 1

        if color is not None:
            self.colors[y, x] = np.uint32(int(color[1:], 16))


    def resize(self, size: tuple[int, int]) -> None:
        copy = (min(self.size[0], size[0]), min(self.size[1], size[1]))
        self.size = size

        resized0 = np.zeros(self.size, dtype=np.uint8)
        resized0[:copy[0], :copy[1]] = self.pixels[:copy[0], :copy[1]]
        self.pixels = resized0

        resized1 = np.zeros(self.size[0], dtype=np.uint8)
        resized1[:copy[0]] = self.dirtys[:copy[0]]
        self.dirtys = resized1

        resized2 = np.full(self.dot_size, 0xffffff, dtype=np.uint32)
        resized2[:copy[0], :copy[1]] = self.pixels[:copy[0], :copy[1]]
        self.colors = resized2


    def clear(self, y: int | None = None) -> None:
        if y is not None:
            self.pixels[y, :] = 0
            self.colors[y, :] = 0xffffff
            self.dirtys[y] = 0
            return

        self.pixels[:, :] = 0
        self.colors[:, :] = 0xffffff
        self.dirtys[:] = 0
