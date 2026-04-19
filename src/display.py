import numpy as np
from dots import Dots


View = tuple[np.ndarray, np.ndarray]


class Display:
    pixels: np.ndarray
    colors: np.ndarray
    layers: int
    size: tuple[int, int]


    def __init__(self, size: tuple[int, int] = (0, 0), layers: int = 1) -> None:

        # Calculate ndarray shape.
        shape = (layers, size[0], size[1])

        # Initialize ndarrays.
        self.pixels = np.full(shape, ' ', dtype='U1')
        self.colors = np.zeros(shape, dtype=np.uint32)

        # Initialize size.
        self.layers = layers
        self.size = size


    def composite(self) -> tuple[np.ndarray, np.ndarray]:

        # Build mask for nonwhitespace characters.
        mask = self.pixels != ' '

        # Map topmost layers.
        top = np.argmax(mask[::-1], axis=0)
        top = (self.layers - 1) - top

        # Broadcast row and column index arrays to gather one element per position.
        rows = np.arange(self.size[0])[:, np.newaxis]
        cols = np.arange(self.size[1])[np.newaxis, :]

        # Gather pixels and colors from topmost layer at each pixel position.
        pixels = self.pixels[top, rows, cols]
        colors = self.colors[top, rows, cols]

        # Blank out pixels where no layer has any content.
        content = mask.any(axis=0)
        pixels[~content] = ' '
        colors[~content] = 0

        return pixels, colors


    def resize(self, size: tuple[int, int]) -> None:

        # Calculate ndarray shape.
        shape = (self.layers, size[0], size[1])

        # Calculate height and width of the copy.
        ch, cw = min(self.size[0], size[0]), min(self.size[1], size[1])

        # Initialize new ndarrays.
        pixels = np.full(shape, ' ', dtype='U1')
        colors = np.zeros(shape, dtype=np.uint32)

        # Copy old data.
        pixels[:, :ch, :cw] = self.pixels[:, :ch, :cw]
        colors[:, :ch, :cw] = self.colors[:, :ch, :cw]

        # Reset old arrays to resized arrays.
        self.pixels = pixels
        self.colors = colors

        # Reset size.
        self.size = size


    def clear(self, layer: int) -> None:

        # Blank out arrays at specified layer.
        self.pixels[layer, :, :] = ' '
        self.colors[layer, :, :] = 0


    def clear_all(self) -> None:

        # Blank out arrays on all layers.
        self.pixels[:, :, :] = ' '
        self.colors[:, :, :] = 0
