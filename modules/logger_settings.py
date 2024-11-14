"""
Модуль настраивает логирование в библиотеке loguru

Def:
    configure_logger: Функция назначает уровень логирования сообщения
                        и настраивает логгер.

"""

import pathlib
import sys

from loguru import logger


def configure_logger(level: str):
    """
    Функция назначает уровень логирования сообщения и настраивает
        логгер.
    """
    # Директория лог файлов
    log_path = pathlib.Path.joinpath(
        pathlib.Path(__file__).absolute().parent.parent,
        "logs/",
        f"{pathlib.Path(__file__).absolute().parent.parent.stem}.log",
    )
    # Максимальный размер файла логирования
    rotation_size = "50 MB"

    logger.remove()
    logger.add(sys.stdout, level=level)
    logger.add(
        log_path,
        level=level,
        rotation=rotation_size,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} |"
        "{module}:{function}:{line}: - {message}",
    )
    logger.debug(
        f"Настройки системы логирования: \n"
        f" путь к лог-файлу:    {log_path}\n"
        f" Уровень логирования: {level}"
    )


__all__ = ["logger"]
