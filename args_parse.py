import argparse
import random
from copy import deepcopy

from defaults import DEFAULT_CONFIG

FUNCTION_PART_COUNT = 2
AFFINE_PARAMS_COUNT = 6


def parse_args() -> argparse.Namespace:
    """Парсер аргументов командной строки."""
    parser = argparse.ArgumentParser(description="Генератор фрактального пламени")

    parser.add_argument("--width", "-w", type=int, help="Ширина выходного изображения")
    parser.add_argument("--height", "-H", type=int, help="Высота выходного изображения")
    parser.add_argument(
        "--seed", "-s", type=float, help="Начальное значение генератора"
    )
    parser.add_argument(
        "--iteration-count", "-i", type=int, help="Количество итераций генерации"
    )
    parser.add_argument("--output-path", "-o", help="Путь для записи PNG")
    parser.add_argument("--threads", "-t", help="Количество потоков", type=int)
    parser.add_argument(
        "--affine-params",
        "-ap",
        type=str,
        help="<a_1>,<b_1>,<c_1>,<d_1>,<e_1>,<f_1>/<a_N>,<b_N>,<c_N>,<d_N>,<e_N>,<f_N>",
    )
    parser.add_argument(
        "--functions",
        "-f",
        type=str,
        help="<функция_N>:<вес_функции>,<функция_N>:<вес_функции>",
    )
    parser.add_argument("--config", "-c", type=str, help="Путь до файла конфигурации")

    return parser.parse_args()


def parse_functions(value: str) -> dict[str, float]:
    """Парсер строки с трансформациями."""
    if value is None:
        return {}

    result = {}

    for item in value.split(","):
        trimmed_item = item.strip()
        if not trimmed_item:
            continue

        parts = trimmed_item.split(":")
        if len(parts) != FUNCTION_PART_COUNT:
            message = f"Неверный формат функции {trimmed_item}"
            raise ValueError(message)

        name, weight = parts
        weight = float(weight)

        result[name] = weight

    return result


def parse_affine_params(value: str) -> list[dict]:
    """Парсер строки с афинными преобразованиями."""
    if not value:
        return []
    result = []
    groups = value.split("/")
    for group in groups:
        trimmed_group = group.strip()
        if not trimmed_group:
            continue

        parts = trimmed_group.split(",")
        if len(parts) != AFFINE_PARAMS_COUNT:
            message = f"Ожидается {AFFINE_PARAMS_COUNT} параметров: {trimmed_group}"
            raise ValueError(message)
        try:
            a, b, c, d, e, f = (float(p) for p in parts)
        except ValueError as err:
            message = f"Невозможно преобразовать параметры в числа: {trimmed_group}"
            raise ValueError(message) from err

        color = (
            random.randint(50, 255),
            random.randint(50, 255),
            random.randint(50, 255),
        )

        result.append({"a": a, "b": b, "c": c, "d": d, "e": e, "f": f, "color": color})

    return result


def _apply_size_config(cfg: dict, size: dict) -> None:
    """Применяет размер из json."""
    if "width" in size:
        cfg["width"] = int(size["width"])
    if "height" in size:
        cfg["height"] = int(size["height"])


def _apply_simple_params(cfg: dict, json_config: dict) -> None:
    """Применяет простые параметры из json."""
    if "iteration_count" in json_config:
        cfg["iteration_count"] = int(json_config["iteration_count"])
    if "output_path" in json_config:
        cfg["output_path"] = str(json_config["output_path"])
    if "threads" in json_config:
        cfg["threads"] = int(json_config["threads"])
    if "seed" in json_config:
        cfg["seed"] = float(json_config["seed"])


def _apply_affine_from_json(cfg: dict, affine_params: list) -> None:
    """Применяет афинные параметры из JSON."""
    cfg["affine_params"] = [
        {
            "a": float(p["a"]),
            "b": float(p["b"]),
            "c": float(p["c"]),
            "d": float(p["d"]),
            "e": float(p["e"]),
            "f": float(p["f"]),
            "color": (
                random.randint(50, 255),
                random.randint(50, 255),
                random.randint(50, 255),
            ),
        }
        for p in affine_params
    ]


def _merge_json_config(cfg: dict, json_config: dict) -> None:
    """Применяет json к cfg."""
    if not json_config:
        return

    size = json_config.get("size", {})
    _apply_size_config(cfg, size)

    _apply_simple_params(cfg, json_config)

    if "functions" in json_config:
        functions = json_config["functions"]
        cfg["functions"] = {f["name"]: float(f["weight"]) for f in functions}

    if "affine_params" in json_config:
        _apply_affine_from_json(cfg, json_config["affine_params"])


def _apply_cli_simple_params(cfg: dict, cli_args: argparse.Namespace) -> None:
    """Применяет простые параметры из аргументов."""
    if cli_args.width is not None:
        cfg["width"] = cli_args.width
    if cli_args.height is not None:
        cfg["height"] = cli_args.height
    if cli_args.iteration_count is not None:
        cfg["iteration_count"] = cli_args.iteration_count
    if cli_args.output_path is not None:
        cfg["output_path"] = str(cli_args.output_path)
    if cli_args.threads is not None:
        cfg["threads"] = cli_args.threads
    if cli_args.seed is not None:
        cfg["seed"] = float(cli_args.seed)


def _apply_cli_functions(cfg: dict, functions_str: str) -> None:
    """Применяет функции из аргументов."""
    if functions_str:
        functions = parse_functions(functions_str)
        if functions:
            cfg["functions"] = functions


def _apply_cli_affine(cfg: dict, affine_str: str) -> None:
    """Применяет афинные параметры из аргументов."""
    if affine_str:
        affine_params = parse_affine_params(affine_str)
        if affine_params:
            cfg["affine_params"] = affine_params


def _merge_cli_config(cfg: dict, cli_args: argparse.Namespace) -> None:
    """Применяет аргументы к cfg ."""
    _apply_cli_simple_params(cfg, cli_args)
    _apply_cli_functions(cfg, cli_args.functions)
    _apply_cli_affine(cfg, cli_args.affine_params)


def merge_config(cli_args: argparse.Namespace, json_config: dict) -> dict:
    """Объединяет конфигурации."""
    cfg = deepcopy(DEFAULT_CONFIG)
    _merge_json_config(cfg, json_config)
    _merge_cli_config(cfg, cli_args)
    return cfg
