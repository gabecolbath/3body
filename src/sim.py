import math
import random
from dataclasses import dataclass


GRAV_CONST = 5
DT_BASE = 1
SOFTENING = 2


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
    tone: str


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


    def update(self) -> None:
        if not self.settings.paused:
            sub_steps = max(1, int(4 * self.settings.speed_mult))
            dt = DT_BASE * self.settings.speed_mult / sub_steps

            self._update_bodies(dt)
            self._update_stars(dt)
            self._update_shooters(dt)

            self.step += 1


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
