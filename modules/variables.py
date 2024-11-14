"""
Модуль содержит статические переменные, которые настраивают
    приложение на моменте запуска.
"""

import pathlib
import re
from os import getenv
from sys import exit

from modules.logger_settings import configure_logger, logger

# ОБЩИЕ ПЕРЕМЕННЫЕ
DEBUG_MODE = getenv("DEBUG", "False").lower() in ("true", "1", "t")
if DEBUG_MODE:
    logger.warning("Запущен отладочный режим\n")

LOG_LEVEL = getenv("LOG_LEVEL", "INFO")
if LOG_LEVEL not in [
    "TRACE",
    "DEBUG",
    "INFO",
    "SUCCESS",
    "WARNING",
    "ERROR",
    "CRITICAL",
]:
    exit("Level is wrong")
else:
    configure_logger(LOG_LEVEL)

TYPE_PARSER = getenv("TYPE_PARSER", "LOCAL").upper() in ("GLOBAL")
if TYPE_PARSER:
    logger.info("Установлен режим парсинга ответа от сайта.\n")
else:
    logger.info("Установлен режим парсинга файлов.\n")

# ПЕРЕМЕННЫЕ ДЛЯ ЗАПРОСА NOTAMS

# a= pathlib.PurePath(__file__).parent.parent
PATH_INPUT_FILES = getenv("PATH_INPUT_FILES")
""" Входная директория с файлами, содержащими резервирования """

PATH_TO_LOCAL_ICAO_LIST = pathlib.Path(
    "D:\Programming\курсы\practic_BS\input_data\ICAO_mini.txt"
)
# "/home/alex/projects/notam-analyzer/services/parser_notams/tests/test_data/icao_list/ICAO.txt"
""" Путь к фалу со списком ЦУВДов. """

URL_REQUEST_HEADER = getenv("URL_REQUEST_HEADER")
""" URL сайта с резервированиями. """
if URL_REQUEST_HEADER is None:
    exit("URL_REQUEST_HEADER is not set")


BASE_REQUEST_HEADER = {
    "User-Agent": "Mozilla/5.0",
    "content-type": "application/x-www-form-urlencoded",
    "accept": "text/html,application/xhtml+xml,application/xml;\
    q=0.9,image/avif, image/webp,image/apng,*/*;\
    q=0.8,application/signed-exchange;v=b3;q=0.9",
}
"""
Часть заголовка запроса.\n

(User-Agent, content-type и т.д.)
"""

ARTCC_LIST_LIMIT = int(getenv("ARTCC_LIST_LIMIT", "50"))
""" Лимит количества ЦУВДов для запроса. По умолчанию равен 50."""

COUNT_REQUEST_LIMIT = int(getenv("COUNT_REQUEST_LIMIT", "5"))
""" Лимит количества попыток при неудачном подключении. """

SLEEP_TIME_REQUEST_NOTAMS = float(getenv("SLEEP_TIME_REQUEST_NOTAMS", "3"))
""" Пауза в секундах между попытками выгрузки NOTAMS. """

# ПЕРЕМЕННЫЕ ДЛЯ РАБОТЫ С БД
TYPE_DB = getenv("TYPE_DB")
""" Тип базы данных. """
if TYPE_DB != "mongodb":
    exit("Database type is not supported or not set")

DATABASE_URL = getenv("DATABASE_URL")
""" URL базы данных и порт. """
if DATABASE_URL is None:
    exit("DATABASE_URL is not set")

DATABASE_NOTAMS_NAME = getenv("DATABASE_NOTAMS_NAME")
""" Имя базы данных NOTAMS. """
if DATABASE_NOTAMS_NAME is None:
    exit("DATABASE_NOTAMS_NAME is not set")

COLLECTION_NOTAMS = getenv("COLLECTION_NOTAMS", "")
""" Коллекция базы данных mongo для NOTAMs. """
if COLLECTION_NOTAMS == "":
    exit("COLLECTION_NOTAMS is not set")

# Паттерны REGEX
REGEX_PERIOD = re.compile(
    r"(?P<day_start>\d\d)\s?"
    r"(?P<month_start>\w\w\w)\s?"
    r"(?P<hour_start>\d\d):(?P<minutes_start>\d\d)\s?"
    r"(?P<year_start>\d\d\d\d)\s?UNTIL\s?"
    r"(?P<day_finish>\d\d)\s?"
    r"(?P<month_finish>\w\w\w)\s?"
    r"(?P<hour_finish>\d\d):(?P<minutes_finish>\d\d)\s?"
    r"(?P<year_finish>\d\d\d\d)"
)
""" Паттерн строки вида '09 AUG 04:14 2022 UNTIL 09 SEP 23:59 2022' """

REGEX_PERIOD_START = re.compile(
    r"(?P<day_start>\d\d)\s?"
    r"(?P<month_start>\w\w\w)\s?"
    r"(?P<hour_start>\d\d):(?P<minutes_start>\d\d)\s?"
    r"(?P<year_start>\d\d\d\d)\s?UNTIL\s?"
)
""" Паттерн строки вида '09 AUG 04:14 2022 UNTIL ' """

REGEX_PERIOD_FINISH = re.compile(
    r"\s?UNTIL\s?(?P<day_finish>\d\d)\s?"
    r"(?P<month_finish>\w\w\w)\s?"
    r"(?P<hour_finish>\d\d):(?P<minutes_finish>\d\d)\s?"
    r"(?P<year_finish>\d\d\d\d)"
)
""" Паттерн строки вида ' UNTIL 09 SEP 23:59 2022' """

REGEX_CREATE = re.compile(
    r"CREATED:\s?(?P<day_create>\d\d)\s?"
    r"(?P<month_create>\w\w\w)\s?"
    r"(?P<hour_create>\d\d):(?P<minutes_create>\d\d)\s?"
    r"(?P<year_create>\d\d\d\d)"
)
"""
Паттерн строки вида 'CREATED: 26 AUG 14:26 2022' """

REGEX_ARTCC = re.compile(r"^[A-Z]{4}$")
"""
Паттерн кода ЦУВД. (например "MHTG").\n

re.compile(r"^[A-Z]{4}$")
"""

REGEX_MANY_SPACE = re.compile(r"\s+")
"""
Паттерн одного или более повторяющегося пробельного символа.\n

re.compile(r"\\s+")
"""

REGEX_START_END_SPACE = re.compile(r"^\s+|\s+$")
"""
Паттерн одного или более пробельного символа в начале и конце строки.\n

re.compile(r"^\\s+|\\s+$")
"""

REGEX_SPACE_POINT = re.compile(r"\s\.")
"""
Паттерн пробельного символа и точки.\n

re.compile(r"\\s\\.")
"""

REGEX_PART_OF = re.compile(
    r"PART (?P<part_number>\d{1,2}) OF (?P<part_all>\d{1,2})"
)
"""
Паттерн строки вида "PART 1 OF 4."\n

re.compile(
    r"PART (?P<part_number>\\d{1,2}) OF (?P<part_all>\\d{1,2})"
)
"""

REGEX_END_PART_OF = re.compile(
    r"END PART (?P<part_number>\d{1,2}) OF (?P<part_all>\d{1,2})"
)
""" Паттерн строки вида "END PART 1 OF 4."\n

re.compile(
    r"END PART (?P<part_number>\\d{1,2}) OF (?P<part_all>\\d{1,2})"
)
"""

REGEX_ISSUED_FOR = re.compile(r"\(ISSUED FOR \w{,4} PART \d{1,2} OF \d{1,2}\)")
"""
Паттерн строки вида "(ISSUED FOR KZMA PART 1 OF 2)"

re.compile(r"\\(ISSUED FOR \\w{,4} PART \\d{1,2} OF \\d{1,2}\\)")
"""

logger.info(f"Тип базы данных:        {TYPE_DB}")
logger.info(f"URL базы данных:         {DATABASE_URL}")
logger.info(f"Имя базы данных NOTAMS: {DATABASE_NOTAMS_NAME}")

logger.info(f"Адрес сайта для запросов: {URL_REQUEST_HEADER}")
logger.debug(f"Лимит количества ЦУВДов для запроса:  {ARTCC_LIST_LIMIT}")
logger.debug(f"Лимит количества попыток подключении: {COUNT_REQUEST_LIMIT}")
logger.debug(
    f"Пауза между попытками:                {SLEEP_TIME_REQUEST_NOTAMS}"
)
