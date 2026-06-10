import math
import numpy as np
from dots import ASPECT, DOTS_WIDTH, DOTS_HEIGHT, Dots
from display import Display, View
from sim import Simulation, Body, Star


# Composite Layers
LAYER_BODIES = 2
LAYER_STARS = 1

# Star Rendering
STAR_CHARS = [ '.', '·', '+', '*']
STAR_BRIGHTNESS = 0.70


class Renderer:
    disp: Display
    view: View
    dots: Dots
    sim: Simulation


    def __init__(self, sim: Simulation) -> None:
        self.disp = Display(layers=3)
        self.view = np.zeros_like(self.disp.pixels), np.zeros_like(self.disp.colors)
        self.dots = Dots()
        self.sim = sim
        self.msize = (0, 0)


    def resize(self, size: tuple[int, int]) -> None:
        self.disp.resize(size)
        self.dots.resize(size)
        self.view = self.disp.composite()


    def start(self) -> None:

        # Initialize star render.
        for star in self.sim.stars:
            x, y = int(math.floor(star.pos.x)), int(math.floor(star.pos.y))
            char = STAR_CHARS[int(math.floor(star.size * len(STAR_CHARS)))]
            self.disp.pixels[LAYER_STARS, y, x] = char


    def update(self) -> None:

        # Composite display layers.
        self.view = self.disp.composite()


    def render_bodies(self) -> None:

        # Clear old dots.
        self.dots.clear()

        # Render a filled circle for each body.
        for body in self.sim.bodies:
            dy, dx = body.pos.y / ASPECT, body.pos.x
            py, px = int(math.floor(dy * DOTS_HEIGHT)), int(math.floor(dx * DOTS_WIDTH))
            rad = int(round(body.rad))
            self.dots.fill_circle(px, py, rad, body.tone)

        # Encode dot pixels.
        pixels, colors = self.dots.encode()

        # Clear layer with old bodies.
        self.disp.clear(LAYER_BODIES)

        # Update display with new values.
        self.disp.pixels[LAYER_BODIES, :, :] = pixels
        self.disp.colors[LAYER_BODIES, :, :] = colors


    def render_stars(self) -> None:

        # Calculate base grey value.
        grey_base = 255 * STAR_BRIGHTNESS

        # Loop through each star and adjust color.
        for star in self.sim.stars:

            # Find stars position on screen and skip if not inbounds.
            x, y = int(math.floor(star.pos.x)), int(math.floor(star.pos.y))
            if not 0 <= x < self.disp.size[1] or not 0 <= y < self.disp.size[0]:
                continue

            # Regenerate blank stars.
            if self.disp.pixels[LAYER_STARS, y, x] == ' ':
                char = STAR_CHARS[int(math.floor(star.size * len(STAR_CHARS)))]
                self.disp.pixels[LAYER_STARS, y, x] = char

            # Get effective luminance accounting for twinkling.
            lum = star.lum + star.twinkle.shine
            lum = lum if lum >= 0 else 0
            lum = lum if lum <= 1 else 1

            # Determine greyscale value of star.
            grey = int(round(grey_base * lum))
            color = ((grey << 16) | (grey << 8) | grey) & 0xffffff

            # Set color of pixel.
            self.disp.colors[LAYER_STARS, y, x] = color
