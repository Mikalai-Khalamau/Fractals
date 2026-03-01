from pathlib import Path

from transformations import TRANSFORMATIONS

COLOR_COMPONENTS_COUNT = 3
COLOR_MAX_VALUE = 255


def _validate_positive_integer(name: str, value: int) -> None:
    """Проверяет, что число положительное."""
    if value <= 0:
        message = f"{name} должна быть положительным числом."
        raise ValueError(message)


def _validate_output_path(output_path: str) -> None:
    """Проверка валидности пути выходного файла."""
    if not output_path.lower().endswith(".png"):
        message = "Выходной путь должен заканчиваться png"
        raise ValueError(message)

    path = Path(output_path)
    parent_dir = path.parent
    if parent_dir != Path() and not parent_dir.exists():
        message = f"Директория {parent_dir} не существует"
        raise ValueError(message)


def _validate_functions(functions: dict) -> None:
    """Проверка функций."""
    available_functions = set(TRANSFORMATIONS.keys())
    for function_name, weight in functions.items():
        if function_name not in available_functions:
            message = f"Функция {function_name} не существует"
            raise ValueError(message)
        if weight <= 0:
            message = f"Вес функции {function_name} должен быть положительным"
            raise ValueError(message)


def _validate_affine_params(affine_params: list[dict]) -> None:
    """Проверяет афинные параметры."""
    required_keys = {"a", "b", "c", "d", "e", "f", "color"}
    for _i, param in enumerate(affine_params):
        missing_keys = required_keys - set(param.keys())
        if missing_keys:
            message = "Не хватает ключей в афинном преобразовании"
            raise ValueError(message)
        color = param["color"]
        _validate_color(color)


def _validate_color(color: tuple[int, int, int]) -> None:
    """Проверка цветов."""
    if len(color) != COLOR_COMPONENTS_COUNT:
        message = "Должно быть три компоненты цвета: R, G, B"
        raise ValueError(message)
    for value in color:
        if not 0 <= value <= COLOR_MAX_VALUE:
            message = "Цвет должен быть в диапазоне [0,255]"
            raise ValueError(message)


def validate_config(config: dict) -> None:
    """Проверка конфига."""
    _validate_positive_integer("width", config.get("width"))
    _validate_positive_integer("height", config.get("height"))
    _validate_positive_integer("iteration_count", config.get("iteration_count"))
    _validate_positive_integer("threads", config.get("threads"))
    output_path = config.get("output_path")
    _validate_output_path(output_path)
    functions = config.get("functions")
    _validate_functions(functions)
    affine_params = config.get("affine_params")
    _validate_affine_params(affine_params)
