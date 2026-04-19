import math
import numpy as np
from dots import ASPECT, DOTS_WIDTH, DOTS_HEIGHT, Dots
from display import Display, View
from sim import Simulation, Body


class Renderer:
    disp: Display
    view: View
    dots: Dots


    def __init__(self) -> None:
        self.disp = Display(layers=3)
        self.view = np.zeros_like(self.disp.pixels), np.zeros_like(self.disp.colors)
        self.dots = Dots()


    def resize(self, size: tuple[int, int]) -> None:
        self.disp.resize(size)
        self.dots.resize(size)
        self.view = self.disp.composite()


    def update(self) -> None:
        self.view = self.disp.composite()


    def render_bodies(self, bodies: list[Body]) -> None:

        # Clear old dots.
        self.dots.clear()

        # Render a filled circle for each body.
        for body in bodies:
            dy, dx = body.pos.y / ASPECT, body.pos.x
            py, px = int(math.floor(dy * DOTS_HEIGHT)), int(math.floor(dx * DOTS_WIDTH))
            rad = int(round(body.rad))
            self.dots.fill_circle(px, py, rad, body.tone)

        # Encode dot pixels.
        pixels, colors = self.dots.encode()

        # Clear layer with old bodies.
        self.disp.clear(0)

        # Update display with new values.
        self.disp.pixels[0, :, :] = pixels
        self.disp.colors[0, :, :] = colors
