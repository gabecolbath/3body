from abc import ABC, abstractmethod
import random
from typing import Generic, TypeVar
import math

from src.rendering.display import Display
from src.rendering.dots import ASPECT, Dots
from src.sim import Vec, Simulation, Body, Star


T = TypeVar('T')


class Renderer(ABC, Generic[T]):
    disp: Display[T]


    def __init__(self) -> None:
        self.disp = Display()


    @abstractmethod
    def resize(self, size: tuple[int, int]) -> None:
        self.disp.resize(size)


    @abstractmethod
    def render(self) -> None:
        pass


    @abstractmethod
    def render_line(self, y: int) -> None:
        pass


class SimulationRenderer(Renderer[None]):
    bodies: BodiesRenderer


    def __init__(self, sim: Simulation) -> None:
        super().__init__()
        self.bodies = BodiesRenderer(sim)


    def resize(self, size: tuple[int, int]) -> None:
        self.disp.resize(size)
        self.bodies.resize(size)


    def render(self) -> None:
        self.disp.clear()
        self.bodies.render()
        for y in range(self.disp.size[0]):
            self.render_line(y)


    def render_line(self, y: int) -> None:
        self.disp[y] = self.bodies.disp[y]


class BodiesRenderer(Renderer):
    sim: Simulation
    dots: Dots


    def __init__(self, sim: Simulation) -> None:
        super().__init__()
        self.sim = sim
        self.dots = Dots()


    def resize(self, size: tuple[int, int]) -> None:
        self.disp.resize(size)
        self.dots.resize(size)


    def render(self) -> None:
        def render_body(body: Body) -> None:
            cen = body.pos
            rad = Vec(body.rad, body.rad / ASPECT)

            r2 = body.rad**2
            by, bx = int(math.ceil(rad.y)), int(math.ceil(rad.x))
            cy, cx = Dots.world_to_dot(cen.y, cen.x)

            for x in range(-bx, bx):
                for y in range(-by, by):
                    if Vec(x, ASPECT * y).mag2() < r2:
                        dy, dx = (cy + y, cx + x)
                        self.dots.dot_set(dy, dx, 1, color=body.tone)


        self.dots.clear()
        for body in self.sim.bodies:
            render_body(body)

        self.disp.clear()
        for y in range(self.dots.size[0]):
            self.render_line(y)


    def render_line(self, y: int) -> None:
        self.disp[y] = self.dots.line(y)


class StarsRenderer(Renderer[Star]):
    sim: Simulation

    def __init__(self, sim: Simulation, n: int):
        super().__init__()
        self.sim = sim


    def resize(self, size: tuple[int, int]) -> None:
        self.disp.resize(size)

