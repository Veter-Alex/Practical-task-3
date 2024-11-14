from time import time

import requests
from dotenv import load_dotenv
from modules.error import DBError, FileError, NetworkError, ParserError
from modules.logger_settings import logger
from modules.parser_global import parser_notams_answer
from modules.variables import (
    ARTCC_LIST_LIMIT,
    BASE_REQUEST_HEADER,
    COUNT_REQUEST_LIMIT,
    SLEEP_TIME_REQUEST_NOTAMS,
    URL_REQUEST_HEADER,
)

load_dotenv()


def get_notams(icao_codes):  # sourcery skip: dict-assign-update-to-union
    dict_notams = {}
    try:
        # Формируем заголовки для запросов со списками  ЦУВДов
        for data_request_header in get_request_headers(icao_codes):
            # Запрос резервирований для списка ЦУВД
            text_notams_answer = request_notams(data_request_header).text
            dict_notams.update(parser_notams_answer(text_notams_answer))
        for item in dict_notams:
            for i in range(len(dict_notams[item])):
                dict_notams[item][i] = dict_notams[item][i].replace(
                    "US", "!!!!!"
                )
        return dict_notams
    except (DBError, ParserError, NetworkError) as err:
        logger.error(err)
    except FileError as err:
        logger.error(err)


def chunks(icao_codes: list[str], chunk_size: int = 50) -> list[list[str]]:
    """
    Функция делит список lst на части по количеству элементов указанных
        в chunk_size

    Args:
        lst (list[str]): список ЦУВД для запроса

    Returns:
        list[list[str]]: список разбитый на части по chunk_size элементов

    Пример:
        lst = MHTG KZDV KZLA KZOA KZAK KZSE KZMA KZNY KZOB KZAU KZFW
        KZAN KZMP KZTL
        chunk_size = 3
    Выход:
        [['MHTG', 'KZDV', 'KZLA'], ['KZOA', 'KZAK', 'KZSE'], ['KZMA',
        'KZNY', 'KZOB'], ['KZAU', 'KZFW', 'KZAN'], ['KZMP', 'KZTL']]
    """
    return [
        icao_codes[i : i + chunk_size]
        for i in range(0, len(icao_codes), chunk_size)
    ]


def get_request_headers(icao_codes) -> list[list[type[str]]]:
    """
    Функция формирует заголовки для запросов.

    Raises:
        main.NetworkError: _description_

    Returns:
        list[list[type[str]]]: список заголовков для запросов

    Пример заголовка для запроса:
        request_headers=
        [[('reportType', 'Report'), ('retrieveLocId', 'MHTG KZDV KZLA'),
          ('actionType', 'notamRetrievalByICAOs'), ('submit', 'View NOTAMs')],
        [('reportType', 'Report'), ('retrieveLocId', 'KZOA KZAK KZSE'),
          ('actionType', 'notamRetrievalByICAOs'), ('submit', 'View NOTAMs')],
        [('reportType', 'Report'), ('retrieveLocId', 'KZMA KZNY KZOB'),
          ('actionType', 'notamRetrievalByICAOs'), ('submit', 'View NOTAMs')],
        [('reportType', 'Report'), ('retrieveLocId', 'KZAU KZFW KZAN'),
          ('actionType', 'notamRetrievalByICAOs'), ('submit', 'View NOTAMs')],
        [('reportType', 'Report'), ('retrieveLocId', 'KZMP KZTL'),
          ('actionType', 'notamRetrievalByICAOs'), ('submit', 'View NOTAMs')]
    """
    try:
        request_headers = []  # список заголовков
        request_header = [str]  # заголовок
        for chunk in chunks(icao_codes, ARTCC_LIST_LIMIT):
            request_header = [
                ("reportType", "Report"),
                ("retrieveLocId", " ".join(chunk)),
                ("actionType", "notamRetrievalByICAOs"),
                ("submit", "View NOTAMs"),
            ]
            # добавляем запрос к списку запросов
            request_headers.append(request_header)
    except Exception as err:
        raise NetworkError(
            f"Ошибка формирования заголовков для запросов. {err}"
        ) from err
    else:
        logger.info("Сформированы заголовки для запросов.")
        return request_headers


def request_notams(data_request_header: list[type[str]]) -> requests.Response:
    """
    Функция выполняет запрос резервирований для списка ЦУВД,
        указанных в заголовке запроса (data_request_header).

    Args:
        data_request_header (list[type[str]]): список ЦУВД для запроса

    Raises:
        main.NetworkError: _description_

    Returns:
        requests.Response: ответ от сайта с резервированиями
    """
    try:
        # Выполнение запроса
        logger.info(f"Выполняется запрос на сайт {URL_REQUEST_HEADER}")
        session = requests.session()
        answer = requests.Response  # Ответ от сайта с резервированиями
        # TODO исправить "type: ignore" если имеет смысл
        answer = session.post(
            URL_REQUEST_HEADER,  # type: ignore
            headers=BASE_REQUEST_HEADER,
            data=data_request_header,  # type: ignore
        )
        # count_request - счетчик для неудачных запросов
        count_request = 2
        while (answer.status_code != 200) and (
            count_request < COUNT_REQUEST_LIMIT
        ):
            logger.error(
                f"Ошибка подключения {answer.status_code}.\n"
                f" Переподключение через {BASE_REQUEST_HEADER}"
                f" секунды.\n Попытка {count_request}"
                f" из {COUNT_REQUEST_LIMIT}."
            )
            # пауза перед следующей попыткой подключения
            time.sleep(SLEEP_TIME_REQUEST_NOTAMS)
            count_request += 1
            session = requests.session()
            answer = session.post(
                URL_REQUEST_HEADER,  # type: ignore
                headers=BASE_REQUEST_HEADER,
                data=data_request_header,  # type: ignore
            )
        if (answer.status_code != 200) and (
            count_request > COUNT_REQUEST_LIMIT
        ):
            raise NetworkError(
                f"Не удалось подключиться к базе данных."
                f" Статус-код: {answer.status_code}\n"
            )
    except Exception as err:
        raise NetworkError(f" Ошибка: {err}") from err
    else:
        logger.info("Ответ от сайта получен..")
        return answer
