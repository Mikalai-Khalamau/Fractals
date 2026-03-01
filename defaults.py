DEFAULT_WIDTH = 1920
DEFAULT_HEIGHT = 1080
DEFAULT_SEED = 5
DEFAULT_ITERATION_COUNT = 2500
DEFAULT_OUTPUT_PATH = "result.png"
DEFAULT_THREADS = 1
DEFAULT_FUNCTIONS = {"linear": 1.0}

DEFAULT_AFFINE_PARAMS = [
    {
        "a": 0.5,
        "b": 0,
        "c": 0,
        "d": 0,
        "e": 0.5,
        "f": 0,
        "color": (255, 100, 100),
    },
    {
        "a": 0.5,
        "b": 0,
        "c": 0.5,
        "d": 0,
        "e": 0.5,
        "f": 0,
        "color": (100, 255, 100),
    },
    {
        "a": 0.5,
        "b": 0,
        "c": 0,
        "d": 0,
        "e": 0.5,
        "f": 0.5,
        "color": (100, 100, 255),
    },
]

DEFAULT_CONFIG = {
    "width": DEFAULT_WIDTH,
    "height": DEFAULT_HEIGHT,
    "seed": DEFAULT_SEED,
    "iteration_count": DEFAULT_ITERATION_COUNT,
    "output_path": DEFAULT_OUTPUT_PATH,
    "threads": DEFAULT_THREADS,
    "functions": DEFAULT_FUNCTIONS.copy(),
    "affine_params": [param.copy() for param in DEFAULT_AFFINE_PARAMS],
}
