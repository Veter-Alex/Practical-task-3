"""
Модуль отвечает за операции с файлами.

Def:
    get_files: Функция формирует список текстовых файлы для обработки.
    get_icao_list: Функция считывает список ЦУВДов из файла.

Raises:
    FileError: Ошибки связанные с проблемой в соединении
"""

import os
from pathlib import Path

from modules.error import FileError
from modules.logger_settings import logger
from modules.parser_global import correcting_and_check_artcc
from modules.variables import PATH_INPUT_FILES, PATH_TO_LOCAL_ICAO_LIST


def get_icao_list(
    PATH_TO_LOCAL_ICAO: Path = PATH_TO_LOCAL_ICAO_LIST,
) -> list[str]:
    """
    Функция считывает список ЦУВДов из файла.

    Вход:
        - файл ICAO.txt пример: "MHTG KZDV KZLA KZOA KZAK"
            * пробел как разделитель для списка
            * используется для тестирования
        - если файла отсутствует,
            то список ЦУВДов считывается в базе данных
            в индивидуальных настройках пользователя
    Выход:
        ['MHTG', 'KZDV', 'KZLA', 'KZOA', 'KZAK']
    """
    # путь к файлу с списком ЦУВД
    # PATH_TO_LOCAL_ICAO = variables.PATH_TO_LOCAL_ICAO_LIST
    if PATH_TO_LOCAL_ICAO.exists():
        logger.info(
            f"Путь к файлу с резервациями {PATH_TO_LOCAL_ICAO}. \n"
            f"Получение списка ЦУВД из файла ..."
        )
        try:
            # Чтения файла со списком ЦУВД
            with open(PATH_TO_LOCAL_ICAO) as f:
                # пробел как разделитель для списка
                icao_list = f.read().split()
        except Exception as err:
            raise FileError(
                f"Ошибка чтения файла со списком ЦУВД.\n Error: {err}"
            ) from err
    else:
        # Если файл со списком ЦУВД отсутствует
        #  чтение производится из базы данных
        #  из настроек конкретного пользователя
        logger.info("Получение списка ЦУВД из базы данных ...")
        try:
            # TODO реализовать подключение к БД и считывание списка ЦУВДов
            #  из настроек конкретного пользователя
            # icao_list = ???
            raise FileError(
                "Не реализовано считывание списка ЦУВД из базы данных."
            )
        except Exception as err:
            raise FileError(
                f"Ошибка чтения списка ЦУВД из базы данных.\n {err}"
            ) from err
    # Корректного списка ЦУВД
    icao_list = [correcting_and_check_artcc(item) for item in icao_list]
    return icao_list


def get_files(
    PATH_INPUT_FILES: str = PATH_INPUT_FILES,  # type: ignore
) -> list[str]:
    """Функция формирует список текстовых файлы для обработки.

    Raises:
        FileError: _description_

    Returns:
        list[str]: список файлов
    """
    try:
        logger.info(
            f"Входная директория с файлами для анализа {PATH_INPUT_FILES}"
        )
        if not os.path.exists(PATH_INPUT_FILES):
            raise FileError(
                "Входная директория с файлами для анализа не задана."
            )
        filelist = []
        for root, dirs, files in os.walk(PATH_INPUT_FILES):
            for file in files:
                if file.endswith(".txt"):
                    filelist.append(os.path.join(root, file))
                    logger.debug(f"Найден файл: {os.path.join(root, file)}")
    except Exception as err:
        raise FileError(
            f"Ошибка формирования списка текстовых файлов.\n Error: {err}"
        ) from err
    else:
        logger.info(f"Найдено файлов для обработки: {len(filelist)}")
        return filelist
