import math
import random
import numpy as np
from dataclasses import dataclass


# Physics Configuration
GRAV_CONST = 5
DT_BASE = 1
SOFTENING = 2

# Bodies Configuration
RADIUS_MIN = 1
RADIUS_MAX = 10
TONES = [
    0xff0000,
    0x00ff00,
    0x0000ff,
]

# Stars Configuration
AVG_DIST_BETWEEN_STARS = 5
TWINKLE_AMPLITUDE = 0.1
TWINKLE_SPEED_MAX = 0.4


@dataclass
class Vec:
    x: float
    y: float


    @staticmethod
    def zeros() -> Vec:
        return Vec(0, 0)


    @staticmethod
    def rand(x_range: tuple[float, float], y_range: tuple[float, float]) -> Vec:
        x = random.uniform(x_range[0], x_range[1])
        y = random.uniform(y_range[0], y_range[1])
        return Vec(x, y)


    def __call__(self) -> tuple[float, float]:
        return (self.x, self.y)


    def __add__(self, other: Vec) -> Vec:
        x = self.x + other.x
        y = self.y + other.y
        return Vec(x, y)


    def __iadd__(self, other: Vec) -> Vec:
        self.x += other.x
        self.y += other.y
        return self


    def __sub__(self, other: Vec) -> Vec:
        x = self.x - other.x
        y = self.y - other.y
        return Vec(x, y)


    def __isub__(self, other: Vec) -> Vec:
        self.x -= other.x
        self.y -= other.y
        return self


    def __mul__(self, scaler: float) -> Vec:
        x = scaler * self.x
        y = scaler * self.y
        return Vec(x, y)


    def __rmul__(self, scaler: float) -> Vec:
        x = scaler * self.x
        y = scaler * self.y
        return Vec(x, y)


    def __imul__(self, scaler: float) -> Vec:
        self.x *= scaler
        self.y *= scaler
        return self


    def __truediv__(self, scaler: float) -> Vec:
        x = self.x / scaler
        y = self.y / scaler
        return Vec(x, y)


    def __itruediv__(self, scaler: float) -> Vec:
        self.x /= scaler
        self.y /= scaler
        return self


    def __floordiv__(self, scaler: float) -> Vec:
        x = self.x // scaler
        y = self.y // scaler
        return Vec(x, y)


    def __ifloordiv__(self, scaler: float) -> Vec:
        self.x //= scaler
        self.y //= scaler
        return self


    def floor(self) -> Vec:
        x = math.floor(self.x)
        y = math.floor(self.y)
        return Vec(x, y)


    def mag(self) -> float:
        x2 = self.x**2
        y2 = self.y**2
        return math.sqrt(x2 + y2)


    def mag2(self) -> float:
        x2 = self.x**2
        y2 = self.y**2
        return x2 + y2


    def dir(self) -> float:
        x = self.x
        y = self.y
        return math.atan2(y, x)


@dataclass
class Body:
    pos: Vec
    vel: Vec
    acc: Vec
    mass: float
    rad: float
    tone: int


@dataclass
class Star:
    pos: Vec
    lum: float
    size: float
    twinkle: Twinkle


    @dataclass
    class Twinkle:
        amplitude: float
        speed: float
        phase: float
        shine: float


@dataclass
class Shooter:
    pos: Vec
    vel: Vec
    life: int


@dataclass
class Settings:
    paused: bool = False
    speed_mult: float = 1.0
    scale: float = 1.0


class Simulation:
    bodies: list[Body]
    stars: list[Star]
    shooters: list[Shooter]
    settings: Settings = Settings()
    step: int = 0


    def __init__(self) -> None:
        self.bodies = []
        self.stars = []
        self.shooters = []


    def start(self, bounds: tuple[int, int]) -> None:

        # Set the initial bounds.
        self.bounds = bounds

        # Call start for each component in the simulation.
        self._start_bodies()
        self._start_stars()


    def update(self) -> None:

        # Skip if the simulation is paused.
        if not self.settings.paused:

            # Calculate the delta time.
            sub_steps = max(1, int(4 * self.settings.speed_mult))
            dt = DT_BASE * self.settings.speed_mult / sub_steps

            # Call update for each component in the simulation.
            self._update_bodies(dt)
            self._update_stars(dt)
            self._update_shooters(dt)

            # Increment the step count.
            self.step += 1


    def new_stars(self, msize: tuple[int, int], nsize: tuple[int, int]) -> None:

        # Unpack size tuples.
        my, mx = msize
        ny, nx = nsize

        # Calculate differences in size and sktip if no dimension is larger.
        dy, dx = (ny - my, nx - mx)
        if dy <= 0 and dx <= 0:
            return

        # Initialize numpy array of random star positions.
        pos = np.array([[], []])

        # Handle the case where height is increased.
        if dy > 0:
            n0 = (dy * mx) // AVG_DIST_BETWEEN_STARS
            p0 = np.zeros((2, n0), dtype=np.float32)
            p0[0, :] = (np.random.rand(1, n0) * dy) + my
            p0[1, :] = np.random.rand(1, n0) * mx
            pos = np.hstack((pos, p0), dtype=np.float32)

        # Handle the case where width is increased.
        if dx > 0:
            n1 = (dx * my) // AVG_DIST_BETWEEN_STARS
            p1 = np.zeros((2, n1), dtype=np.float32)
            p1[0, :] = np.random.rand(1, n1) * my
            p1[1, :] = (np.random.rand(1, n1) * dx) + mx
            pos = np.hstack((pos, p1), dtype=np.float32)

        # Handle the case where both are increased.
        if dy > 0 and dx > 0:
            n2 = (dx * dy) // AVG_DIST_BETWEEN_STARS



    def _start_bodies(self) -> None:
        for i in range(3):
            self.bodies.append(Body(
                pos=Vec.rand((0, self.bounds[1]), (0, self.bounds[0])),
                vel=Vec.zeros(),
                acc=Vec.zeros(),
                mass=1,
                # rad=random.uniform(RADIUS_MIN, RADIUS_MAX),
                rad=7,
                tone=TONES[i],
            ))


    def _start_stars(self) -> None:

        # Calculate total number of stars.
        n = (self.bounds[0] * self.bounds[1]) // AVG_DIST_BETWEEN_STARS**2

        # Generate random stars.
        for _ in range(n):
            self.stars.append(Star(
                pos=Vec.rand((0, self.bounds[1]), (0, self.bounds[0])),
                lum=random.uniform(0, 1),
                size=random.uniform(0, 1),
                twinkle=Star.Twinkle(
                    amplitude=TWINKLE_AMPLITUDE,
                    speed=random.uniform(0, TWINKLE_SPEED_MAX),
                    phase=random.uniform(0, math.pi),
                    shine=0,
                )
            ))


    def _update_acc(self) -> None:
        # Skip if these is one or less body.
        if len(self.bodies) <= 1:
            return

        # Reset accelerations to zero.
        for bod in self.bodies:
            bod.acc = Vec.zeros()

        # Update accelerations from gravitational interactions.
        for bod0 in self.bodies[0:]:
            for bod1 in self.bodies[1:]:
                delta = bod1.pos - bod0.pos
                dist2 = delta.mag2()
                dist1 = math.sqrt(dist2)
                f = GRAV_CONST / (dist1 * dist2 + SOFTENING)
                bod0.acc += f * bod1.mass * delta
                bod1.acc -= f * bod0.mass * delta


    def _update_bodies(self, dt: float) -> None:
        # First update to accelerations.
        self._update_acc()

        # Half-step velocities and update positions.
        for bod in self.bodies:
            bod.vel += 0.5 * dt * bod.acc
            bod.pos += dt * bod.vel

        # Second update to accelerations.
        self._update_acc()

        # Half-step velocities.
        for bod in self.bodies:
            bod.vel += 0.5 * dt * bod.acc


    def _update_stars(self, dt: float) -> None:
        # Calculate current time.
        t = dt * self.step

        # Update twinkle.
        for star in self.stars:
            amplitude = star.twinkle.amplitude
            speed = star.twinkle.speed
            phase = star.twinkle.phase
            star.twinkle.shine = amplitude * math.sin((speed * t) + phase)


    def _update_shooters(self, dt: float) -> None:
        # Update positions.
        for shooter in self.shooters:
            shooter.pos += dt * shooter.vel
            shooter.life -= 1
