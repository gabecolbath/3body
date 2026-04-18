import math
import random
import numpy as np

from rich.style import Style
from textual.app import App, ComposeResult
from src.sim import Vec, Simulation, Body, Star
from src.rendering.renderer import SimulationRenderer

from textual.widget import Widget
from textual.events import Resize
from textual.strip import Strip
from rich.segment import Segment


AVG_DIST_BETWEEN_STARS = 3


def initialize_bodies(size: tuple[int, int]) -> list[Body]:
    colors = [
        '#ff0000',
        '#00ff00',
        '#0000ff',
    ]
    bodies = []
    for i in range(3):
        bodies.append(Body(
            pos=Vec.rand((0, size[1]), (0, size[0])),
            vel=Vec.zeros(),
            acc=Vec.zeros(),
            mass=1,
            rad=7,
            tone=colors[i],
        ))
    return bodies


def initialize_stars(size: tuple[int, int]) -> list[Star]:
    n = int((size[0] * size[1]) // (AVG_DIST_BETWEEN_STARS**2))
    return [Star(
        pos=Vec.rand((0, size[1]), (0, size[0])),
        lum=random.uniform(0, 1),
        size=random.uniform(0, 1),
        twinkle=Star.Twinkle(
            amplitude=0.25,
            speed=1,
            phase=random.uniform(0, math.pi),
            shine=0,
        )
    ) for _ in range(n)]


class SimulationWidget(Widget):
    sim: Simulation
    rend: SimulationRenderer
    _initialized_size: bool = False


    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.sim = Simulation()
        self.rend = SimulationRenderer(self.sim)

        init_size = (self.size.height, self.size.width)
        self.rend.resize(init_size)


    def on_mount(self) -> None:
        self.set_interval(1 / 60, self.tick)


    def tick(self) -> None:
        self.sim.update()
        self.rend.render()
        self.refresh()


    def on_resize(self, event: Resize) -> None:
        size = (event.size.height, event.size.width)
        self.rend.resize(size)

        def on_first_resize():
            self.sim.bodies = initialize_bodies(size)
            self.sim.stars = initialize_stars(size)

        if not self._initialized_size:
            on_first_resize()
            self._initialized_size = True

        self.refresh()


    def render_line(self, y: int) -> Strip:
        if y >= self.rend.disp.size[0]:
            return Strip.blank(self.size.width, Style(bgcolor="#000000"))

        line = self.rend.disp[y]
        segs = [Segment(px.char, Style(bgcolor="#000000", color=px.color)) for px in line.pixels]
        return Strip(segs).simplify()


class ThreeBodyApp(App):
    def on_mount(self) -> None:
        self.screen.styles.background = "#000000"


    def compose(self) -> ComposeResult:
        yield SimulationWidget()


if __name__ == "__main__":
    app = ThreeBodyApp()
    app.run()
