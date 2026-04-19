import numpy as np


ASPECT = 1.3
DOTS_WIDTH = 2
DOTS_HEIGHT = 4
KANTENJI_LOOKUP = np.array([chr(0x2800 + i) for i in range(256)], dtype='U1')

BIT_WEIGHTS = np.array([
    [1,    8],
    [2,   16],
    [4,   32],
    [64, 128],
], dtype=np.uint8)



class Dots:
    pixels: np.ndarray
    colors: np.ndarray
    size: tuple[int, int]


    @property
    def shape(self) -> tuple[int, int]:
        return self.pixels.shape


    def __init__(self, size: tuple[int, int] = (0, 0)) -> None:

        # Calculate ndarray shape.
        shape = (size[0] * DOTS_HEIGHT, size[1] * DOTS_WIDTH)

        # Initialize ndarrays.
        self.pixels = np.zeros(shape, dtype=np.bool)
        self.colors = np.zeros(shape, dtype=np.uint32)

        # Initialize size.
        self.size = size


    def encode(self) -> tuple[np.ndarray, np.ndarray]:

        # Reshape into character blocks: (rows, 4, cols, 2)
        rows, cols = self.size
        pixels = self.pixels.reshape(rows, 4, cols, 2)
        colors = self.colors.reshape(rows, 4, cols, 2)

        # Kantenji encoding
        # encoded = np.einsum('iRjC,RC->ij', pixels.astype(np.uint8), BIT_WEIGHTS, dtype=np.uint8, casting='unsafe')
        encoded = (pixels.astype(np.uint8) * BIT_WEIGHTS[np.newaxis, :, np.newaxis, :]).sum(axis=(1, 3))
        chars = np.vectorize(chr)(encoded.astype(np.uint32) | 0x2800)
        chars[encoded == 0] = ' '

        # Color averaging
        counts = np.maximum(pixels.sum(axis=(1, 3)), 1)
        colors_avg = ((colors.astype(np.float32) * pixels).sum(axis=(1, 3)) / counts).astype(np.uint32)

        return chars, colors_avg


    def resize(self, size: tuple[int, int]) -> None:

        # Calculate new ndarray shape.
        old_shape = self.shape
        new_shape = (size[0] * DOTS_HEIGHT, size[1] * DOTS_WIDTH)

        # Calculate and width of the copy.
        cr, cc = min(old_shape[0], new_shape[0]), min(old_shape[1], new_shape[1])

        # Initialize new arrays.
        pixels = np.zeros(new_shape, dtype=np.bool)
        colors = np.zeros(new_shape, dtype=np.uint32)

        # Copy old data.
        pixels[:cr, :cc] = self.pixels[:cr, :cc]
        colors[:cr, :cc] = self.colors[:cr, :cc]

        # Reset old arrays to resized arrays.
        self.pixels = pixels
        self.colors = colors

        # Update size.
        self.size = size


    def clear(self) -> None:

        # Blank out arrays.
        self.pixels[:, :] = 0
        self.colors[:, :] = 0


    def valid_row(self, row: int) -> bool:

        # Check if row is between 0 and height.
        return 0 <= row < self.shape[0]


    def valid_col(self, col: int) -> bool:

        # Check if col is between 0 and width.
        return 0 <= col < self.shape[1]


    def fill_circle(self, cx: int, cy: int, rad: int, color: int = 0xffffff) -> None:

        # Calculate squared radius and boundaries.
        rad2 = rad**2
        n = rad + 1

        # Loop through all pixels in a padded boundary around circle.
        for y in range(-n, n):

            # Row relative to the center.
            row = cy + y

            # Skip if not inbounds.
            if not self.valid_row(row):
                continue

            for x in range(-n, n):

                # Col relative to the center.
                col = cx + x

                # Skip if not inbounds.
                if not self.valid_col(col):
                    continue

                # Draw pixel within radius.
                dist2 = x**2 + (y * ASPECT)**2
                if dist2 < rad2:
                    self.pixels[row, col] = 1
                    self.colors[row, col] = color
