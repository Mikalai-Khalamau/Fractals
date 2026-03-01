import json
import sys
from pathlib import Path

from args_parse import merge_config, parse_args
from args_validation import validate_config
from flame_generator import FlameGenerator
from logger import logger


def load_json_config(config_path: str) -> dict:
    """Загружаем конфигурацию из JSON."""
    if not config_path:
        return {}
    config_file = Path(config_path)
    if not config_file.exists():
        message = "Не найден файл конфигурации."
        logger.error(message)
        return {}
    try:
        with config_file.open(encoding="utf-8") as file:
            json_config = json.load(file)
    except json.decoder.JSONDecodeError as e:
        message = f"Ошибка парсинга JSON {e}"
        logger.error(message)
        return {}

    logger.info("Файл конфигурации загружен.")
    return json_config


def main() -> int:
    """Основная функция программы."""
    try:
        cli_args = parse_args()
        logger.info("Распарсил аргументы командной строки.")

        json_config = cli_args.config
        if json_config:
            json_config = load_json_config(json_config)

        cfg = merge_config(cli_args, json_config)
        logger.info("Объединены конфигурации.")

        validate_config(cfg)

        generator = FlameGenerator(
            width=cfg["width"],
            height=cfg["height"],
            iterations=cfg["iteration_count"],
            seed=int(cfg["seed"]),
        )
        generator.set_threads(cfg["threads"])
        logger.info("Генератор инициализирован.")

        generator.generate(
            affine_transforms=cfg["affine_params"],
            function_weights=cfg["functions"],
            output_path=cfg["output_path"],
        )

        logger.info("Изображение создано и сохранено.")

    except FileNotFoundError as e:
        logger.error(f"Файл конфигурации не найден: {e}")
        return 2
    except TypeError as e:
        logger.error(f"Ошибка типа данных: {e}")
        return 2
    except ValueError as e:
        logger.error(f"Ошибка конфигурации: {e}")
        return 2
    except KeyError as e:
        logger.error(f"Отсутствует ключ: {e}")
        return 2
    else:
        return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
