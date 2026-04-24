import numpy as np
from time import time

from display import Display
from render import Renderer
from sim import Simulation


from textual.app import App, ComposeResult
from textual.widget import Widget
from textual.events import Resize
from textual.strip import Strip
from rich.segment import Segment
from rich.style import Style


FPS = 60


class SimulationWidget(Widget):
    sim: Simulation
    rend: Renderer
    view: tuple[np.ndarray, np.ndarray]
    started: bool
    time: float
    fps: float


    def __init__(self, **kwargs) -> None:

        # Initialize parent class.
        super().__init__(**kwargs)

        # Initalize simulation, renderer, and view.
        self.sim = Simulation()
        self.rend = Renderer(self.sim)

        # Initialize start flag.
        self.started = False

        # Initialize time and fps.
        self.time = time()
        self.fps = FPS


    def on_mount(self) -> None:

        # Call tick at target fps.
        self.set_interval(1 / FPS, self.on_tick)


    def on_tick(self) -> None:

        # Update simulation.
        self.sim.update()

        # Render simulation and cache view.
        self.rend.render_bodies()
        self.rend.render_stars()
        self.rend.update()

        # Refresh widget.
        self.refresh()

        # Update time and fps.
        latest = time()
        elapsed = latest - self.time
        self.time = latest
        self.fps = 1 / elapsed


    def on_resize(self, event: Resize) -> None:

        # Get resize shape.
        size = (event.size.height, event.size.width)

        # Resize display in renderer.
        self.rend.resize(size)

        # Check if this is the first resize and call start if it is.
        if not self.started:
            self.on_start()

        # Refresh widget.
        self.refresh()


    def on_start(self) -> None:

        # Get screen size.
        size = self.size.height, self.size.width

        # Initialize simulation.
        self.sim.start(size)

        # Start rendering.
        self.rend.start()

        # Reset start flag.
        self.started = True


    def render_line(self, y: int) -> Strip:

        # Render FPS Counter.
        if y == 0:
            return Strip([Segment(f"FPS: {self.fps:02}", Style(color="#ff0000", bgcolor="#000000"))], self.size.width)

        # Get display size.
        h, w = self.rend.disp.size

        # Skip line if not inbounds.
        if w == 0 or not 0 <= y < h:
            return Strip.blank(w)

        # Get pixels and colors from view.
        pixels, colors = self.rend.view[0][y], self.rend.view[1][y]

        # Group runs of same color.
        bounds = np.flatnonzero(np.diff(colors)) + 1
        starts = np.concatenate(([0], bounds))
        ends = np.concatenate((bounds, [w]))

        # Breakdown pixels into segments.
        segs = []
        for start, end in zip(starts, ends):
            text = ''.join(pixels[start:end])
            style = Style(color=f"#{colors[start]:06x}", bgcolor="#000000")
            segs.append(Segment(text, style))

        return Strip(segs)


class ThreeBodyApp(App):
    def compose(self) -> ComposeResult:
        yield SimulationWidget()


if __name__ == "__main__":
    app = ThreeBodyApp()
    app.run()
