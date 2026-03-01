import math


def linear(x: float, y: float) -> tuple[float, float]:
    """Линейное."""
    return x, y


def sinusoidal(x: float, y: float) -> tuple[float, float]:
    """Синус."""
    return math.sin(x), math.sin(y)


def spherical(x: float, y: float) -> tuple[float, float]:
    """Сферическое."""
    r_squared = x**2 + y**2 + 1e-9
    return x / r_squared, y / r_squared


def swirl(x: float, y: float) -> tuple[float, float]:
    """Спиральное."""
    r_squared = x**2 + y**2 + 1e-9
    return (
        x * math.sin(r_squared) - y * math.cos(r_squared),
        x * math.cos(r_squared) + y * math.sin(r_squared),
    )


def horseshoe(x: float, y: float) -> tuple[float, float]:
    """Подкова."""
    r = math.sqrt(x**2 + y**2) + 1e-9
    return (x**2 - y**2) / r, 2 * x * y / r


def polar(x: float, y: float) -> tuple[float, float]:
    """Полярное."""
    theta = math.atan2(y, x)
    r = math.sqrt(x**2 + y**2) + 1e-9
    return theta / math.pi, r - 1


def handkerchief(x: float, y: float) -> tuple[float, float]:
    """Носовой платок."""
    theta = math.atan2(y, x)
    r = math.sqrt(x**2 + y**2) + 1e-9
    return math.sin(theta + r) * r, math.cos(theta - r) * r


def heart(x: float, y: float) -> tuple[float, float]:
    """Сердце."""
    theta = math.atan2(y, x)
    r = math.sqrt(x**2 + y**2) + 1e-9
    return math.sin(theta * r) * r, (-1) * math.cos(theta * r) * r


def disc(x: float, y: float) -> tuple[float, float]:
    """Диск."""
    theta = math.atan2(y, x)
    r = math.sqrt(x**2 + y**2) + 1e-9
    return (
        math.sin(math.pi * r) * theta / math.pi,
        math.cos(math.pi * r) * theta / math.pi,
    )


def fisheye(x: float, y: float) -> tuple[float, float]:
    """Рыбий глаз."""
    r = math.sqrt(x**2 + y**2) + 1e-9
    return 2 * y / (r + 1), 2 * x / (r + 1)


def tangent(x: float, y: float) -> tuple[float, float]:
    """Тангенциальное."""
    return math.sin(x) / (math.cos(y) + 1e-9), math.atan(y)


def cross(x: float, y: float) -> tuple[float, float]:
    """Крест."""
    return (
        math.sqrt(1 / ((x**2 - y**2) ** 2)) * x,
        math.sqrt(1 / ((y**2 - x**2) ** 2)) * y,
    )


TRANSFORMATIONS = {
    "linear": linear,
    "sinusoidal": sinusoidal,
    "spherical": spherical,
    "swirl": swirl,
    "horseshoe": horseshoe,
    "polar": polar,
    "handkerchief": handkerchief,
    "heart": heart,
    "disc": disc,
    "fisheye": fisheye,
    "tan": tangent,
    "cross": cross,
}
