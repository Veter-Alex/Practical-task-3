"""
Модуль отвечает за операции парсинга данных.

Def:
    correcting_and_check_artcc: Функция корректирует строку с кодом ЦУВД
        и проверяет ее валидность.
    correcting_notam: Функция исправляет опечатки и приводит текст
        резервирования к унифицированному виду.
    glue_notams: Функция объединяет составные резервирования.
    parser_notam_local: Функция выделяет резервирования из текста.
    parser_notams_answer: Функция выделяет резервирования
                            из ответа от сайта.
    get_notam_number: Функция выделяет номер резервирования из текста.
    get_notam_create: Функция выделяет дату создания резервирования
                            из текста.
    get_notam_start: Функция выделяет дату начала резервирования
                            из текста.
    get_notam_end: Функция выделяет дату окончания резервирования
                            из текста.
    notam_to_json: Функция парсит текст резервирования на составляющие
        и формирует json структуру для записи в базу данных.

Raises:
    ParserError: Все ошибки парсинга данных.
"""

import datetime
from re import search, sub
from typing import List, Optional, Union

import pytz
from bs4 import BeautifulSoup
from modules.error import ParserError
from modules.logger_settings import logger
from modules.variables import (
    REGEX_ARTCC,
    REGEX_CREATE,
    REGEX_END_PART_OF,
    REGEX_ISSUED_FOR,
    REGEX_MANY_SPACE,
    REGEX_PART_OF,
    REGEX_PERIOD_FINISH,
    REGEX_PERIOD_START,
    REGEX_SPACE_POINT,
    REGEX_START_END_SPACE,
)


def correcting_and_check_artcc(artcc: str) -> Optional[str]:
    """
    This function corrects and checks the validity of the ARTCC code.

    Args:
        artcc (str): string with the ARTCC code (e.g. MGHT)

    Returns:
        str: the ARTCC code, consisting of four uppercase Latin
            letters [A-Z], without spaces (e.g. MGHT)

    Example:
        >>> correcting_and_check_artcc("MgHT ")
        "MGHT"
    """
    # Convert to uppercase and remove spaces
    artcc = sub(r"\s", "", artcc.upper())

    # Check if ARTCC code is valid
    if not search(REGEX_ARTCC, artcc):
        logger.warning(
            f"Incorrect ARTCC code format in the list. artcc: {artcc}"
        )
        artcc = ""
    return artcc


def correcting_notam(value: str) -> str:
    """
    This function corrects typos and standardizes the reservation
        NOTAM text.

    Args:
        value (str): the reservation text

    Returns:
        str: the reservation text in uppercase,
            with excess spaces removed and typos corrected
    """
    # Fix typos in "CREATED: 26 AUG 14:26 2022"
    value = sub(
        REGEX_CREATE,
        r" CREATED: \g<day_create> \g<month_create> "
        r"\g<hour_create>:\g<minutes_create> \g<year_create>",
        value,
    )
    # Fix typos in "09 AUG 04:14 2022 UNTIL"
    value = sub(
        REGEX_PERIOD_START,
        r" \g<day_start> \g<month_start> \g<hour_start>:\g<minutes_start> "
        r"\g<year_start> UNTIL ",
        value,
    )
    # Fix typos in "UNTIL 09 SEP 23:59 2022"
    value = sub(
        REGEX_PERIOD_FINISH,
        r" UNTIL \g<day_finish> \g<month_finish> "
        r"\g<hour_finish>:\g<minutes_finish> \g<year_finish> ",
        value,
    )
    # Convert to uppercase
    value = value.upper()
    # Replace multiple spaces with a single space
    value = sub(REGEX_MANY_SPACE, " ", value)
    # Remove leading and trailing spaces
    value = sub(REGEX_START_END_SPACE, "", value)
    # Replace space followed by a dot with just a dot
    value = sub(REGEX_SPACE_POINT, r".", value)
    return value


def correcting_glue_notams(value_temp: str) -> str:
    """
    This function corrects and standardizes the text of concatenated
    notams after merging composite notams.

    Args:
        value_temp (str): the text of the concatenated notams

    Returns:
        str: the cleaned text of the notams without extra characters
    """
    # Pattern REGEX_ISSUED_FOR like "(ISSUED FOR KZMA PART 1 OF 2)"
    # replace with a space
    value_temp = sub(REGEX_ISSUED_FOR, " ", value_temp)

    # Pattern REGEX_END_PART_OF like "END PART 1 OF 2."
    # replace with a space
    value_temp = sub(REGEX_END_PART_OF, " ", value_temp)

    # Pattern REGEX_PART_OF like "PART 1 OF 2."
    # replace with a space
    value_temp = sub(REGEX_PART_OF, " ", value_temp)

    # Search for duplicates parts text from the beginning
    # of the notam text
    dublicate_str = ""
    j = 0
    # Add one character at a time and check for duplicates.
    # By the end of the loop, "duplicate_str" contains a string
    # like "FDC 3/9739 - CA..AIRSPACE COYOTE WELLS, CA..",
    # which repeats more than once in the text
    while dublicate_str + value_temp[j] in value_temp[j:]:
        # ? что быстрее
        # dublicate_str += value_temp[j]
        dublicate_str = f"{dublicate_str}{value_temp[j]}"
        j += 1
    # Delete all duplicates and add one duplicate to the beginning
    if len(dublicate_str) > 4:
        value_temp = dublicate_str + value_temp.replace(dublicate_str, " ")

    # Search for duplicates parts text from the end
    dublicate_str = ""
    j = len(value_temp) - 1
    # Add one character at a time starting from the last character
    # and check for duplicates. By the end of the loop,
    # "duplicate_str" contains a string like # "02 JUL 11:00 2023
    # UNTIL 06 JAN 09:00 2024. CREATED: 29 JUN 14:46 2023",
    # which repeats more than once in the text
    while value_temp[j] + dublicate_str in value_temp[:j]:
        dublicate_str = f"{value_temp[j]}{dublicate_str}"
        j -= 1
    # Delete all duplicates and add one duplicate to the end
    value_temp = value_temp.replace(dublicate_str, " ") + dublicate_str

    # Replace multiple spaces with a single space
    value_temp = sub(REGEX_MANY_SPACE, " ", value_temp)
    # Remove leading and trailing spaces
    value_temp = sub(REGEX_START_END_SPACE, "", value_temp)
    # Replace space followed by a dot with just a dot
    value_temp = sub(REGEX_SPACE_POINT, r".", value_temp)
    return value_temp


def glue_notams(values: list[str]) -> list[str]:
    """
    Функция объединяет составные резервирования.

    Args:
        values (list[str]): список резервирований

    Raises:
        ParserError: _description_

    Returns:
        list[str]: список резервирований

    Составные резервирования объединяются в одно.
    Вторая и последующие части после объединения удаляются.
    """
    # Обрабатываем список резервирований
    for i, value in enumerate(values):
        # Ищем  резервирования состоящие из  нескольких частей
        #  и  объединяем в одно  резервирование
        # паттерн вида "PART 1 OF 2."
        match = search(REGEX_PART_OF, value)
        if (value != "") and match:
            try:
                # получаем количество составных частей
                # указанных в тексте: "PART 1 OF 2." - например 2
                parts = int(match.group("part_all"))
                notam_number = get_notam_number(value)
                logger.debug(
                    f"Объединение резервирования {notam_number},"
                    f" состоящего из {parts} частей."
                )
                # цикл  по количеству частей
                value_temp = ""
                j = 0
                end_cycle = False
                while not end_cycle:
                    match = search(REGEX_PART_OF, values[i + j])
                    value_temp = " ".join([value_temp, values[i + j]])
                    # присваиваем очередному резервированию
                    # из числа составных значение ""
                    values[i + j] = ""
                    j += 1
                    if int(match.group("part_number")) == int(
                        match.group("part_all")
                    ) or not search(REGEX_PART_OF, values[i + j]):
                        end_cycle = True

                # корректируем результирующее резервирование
                #  и присваиваем первому из составных резервирований
                value_temp = correcting_glue_notams(value_temp)
                values[i] = correcting_notam(value_temp)
            except Exception as err:
                raise ParserError(
                    f"Ошибка объединения составных резервирований.\n"
                    f"{err}\n"
                    f"Резервирование: \n"
                    f"{value}\n"
                ) from err
            else:
                logger.debug(
                    f"Резервирование {notam_number},"
                    f" состоящее из {parts} частей объединено."
                )
    # отфильтровываем список values,
    #  чтобы исключить элементы ""
    values = [value for value in values if value != ""]
    return values


def parser_notams_answer(
    text_notams_answer: str,
) -> dict[str, list[str]]:
    """
    Фугкция парсит ответ от сайта и выделяет резервирования.

    Args:
        text_notams_answer (str): ответ от сайта

    Returns:
        dict[str, list[str]]: Словарь, в котором ключ - ИКАО код ЦУВД, а значение - список резервирований.
    """
    try:
        # Parse the answer using BeautifulSoup
        bs = BeautifulSoup(text_notams_answer, "lxml")
        main_table = bs.div.table.tr

        # Find all tables containing reservations
        tables = [
            table
            for table in main_table.find_all("table")
            if table.find_all("td", "textBlack12")
        ]

        notams = {}
        for table in tables:
            if table.find("td", class_="textBlack12").input:
                # Get the ID of the reservation
                id_k = table.find("td", class_="textBlack12").input["id"]

                # Log the ID
                logger.info(f"Получение резервирований для ИКАО кода: {id_k}")

                # Extract the reservations for the ID
                values = [
                    td.pre.text.replace("\n", "")
                    for td in table.find_all("td", "textBlack12")
                    if td.pre is not None
                ]

                # Correct and glue the reservations
                values = [correcting_notam(value) for value in values]
                values = glue_notams(values)

                # Add the reservations to the dictionary
                notams[id_k] = values
    except Exception as err:
        # Raise an error if there is an exception
        raise ParserError(
            f"Ошибка при разборе ответа с веб-сайта.\n" f"Error: {err}"
        ) from err
    else:
        # Log the number of reservations found
        logger.info(
            f"Разбор завершен. "
            f"Найдены резервирования для {len(notams.values())} кодов ИКАО."
        )
        return notams


def get_notam_number(notam: str) -> Optional[str]:
    """
    Extracts the reservation number from the NOTAM text.

    Args:
        notam (str): the reservation text

    Returns:
        str: the reservation number
    """
    # Log the extraction process
    logger.debug("Extracting number from NOTAM: %s...", notam[:15])

    try:
        # Split the NOTAM text into tokens
        tokens = notam.split()

        if "FDC" in tokens[0]:
            # Reservation format:
            #  FDC 1/4403 (A0136/21) - TX AIRSPACE BROWNSVILLE...
            # If the first token contains "FDC",
            #  then the reservation number is formed
            #  by the first two tokens
            notam_number = f"{tokens[0]} {tokens[1]}"
        else:
            # Reservation format:
            #  A0391/04 (12/049) - QWEXX. CARF NR.1227 ON - KODIAK ....
            # Otherwise, the reservation number is the first token
            notam_number = tokens[0]

        # Log the extracted reservation number
        logger.debug("number: %s", notam_number)

        # Return the reservation number
        return notam_number

    except Exception as err:
        # If an error occurs during the extraction process,
        # raise a ParserError with the error message
        raise ParserError(
            f"Error extracting reservation number from NOTAM text:\n" f"{err}"
        ) from err


def get_notam_create(notam: str) -> Union[str, datetime.datetime]:
    """
    Extracts the reservation creation date from the NOTAM text.

    Args:
        notam (str): the reservation text

    Raises:
        ParserError: if there is an error parsing the date

    Returns:
        datetime.datetime: the reservation creation date
    """
    logger.debug(
        f"Extracting creation date from NOTAM text: "
        f"{notam[:15]}...{notam[-15:]}"
    )

    match = search(REGEX_CREATE, notam)
    if match:
        create_date_time = match.group(0).replace("CREATED: ", "")
        notam_create = pytz.utc.localize(
            datetime.datetime.strptime(create_date_time, "%d %b %H:%M %Y")
        )
    else:
        logger.warning(
            f"Error extracting reservation creation date from "
            f"NOTAM text: {notam[:15]}...{notam[-15:]}"
        )
        notam_create = "N/A"

    logger.debug(f"Creation date: {notam_create}")
    return notam_create


def get_notam_start(notam: str) -> Union[str, datetime.datetime]:
    """
    Extracts the start date of the reservation from the NOTAM text.

    Args:
        notam (str): the NOTAM text

    Raises:
        ParserError: if there is an error parsing the text

    Returns:
        datetime.datetime: the start date of the reservation
    """
    logger.debug(
        "Extracting start date from reservation text: "
        f"{notam[:7]}...{notam[-75:]}"
    )

    try:
        match = search(
            REGEX_PERIOD_START,
            notam,
        )
        if match:
            # Get the start date and time of the reservation
            # by searching for the pattern "09 AUG 04:14 2022 UNTIL"
            # and removing " UNTIL " (deleting it)
            start_date_time = match.group(0).replace(" UNTIL ", "")
            # Convert the string to a datetime object
            # and set the UTC timezone
            notam_start = pytz.utc.localize(
                datetime.datetime.strptime(
                    start_date_time,
                    "%d %b %H:%M %Y",
                )
            )
        elif "WIE UNTIL" in notam:
            # WIE (With Immediate Effect) - immediate effect
            #  NOTAM, in this case "notam_start" is set
            #  to the creation date of the reservation
            notam_start = get_notam_create(notam)
        elif "WEF UNTIL" in notam:
            # WEF (With Effect From) - effective from...
            notam_start = "WEF"
        else:
            logger.warning(
                "Error getting start date of reservation from "
                " reservation text."
            )
            notam_start = "N/A"
    except Exception as err:
        raise ParserError(
            "Error getting start date of reservation from NOTAM text.\n"
            f"Error: {err}"
        ) from err
    else:
        logger.debug(f"Start date: {notam_start}")
        return notam_start


def get_notam_end(notam: str) -> Union[str, datetime.datetime]:
    """
    Extracts the end date of a reservation from the text.

    Args:
        notam (str): the reservation text

    Raises:
        ParserError: if there is an error parsing the text

    Returns:
        Union[str, datetime.datetime]: the end date of the reservation
    """
    logger.debug(
        f"Extracting end date from reservation text: "
        f"{notam[:7]}...{notam[-75:]}"
    )
    try:
        match = search(
            REGEX_PERIOD_FINISH,
            notam,
        )
        if match:
            # Get the end date and time of the reservation
            # search for the pattern " UNTIL 09 SEP 23:59 2022"
            # remove " UNTIL " (delete it)
            end_date_time = match.group(0).replace(" UNTIL ", "")
            # Convert the string to a datetime object
            # set the UTC timezone
            notam_end = pytz.utc.localize(
                datetime.datetime.strptime(
                    end_date_time,
                    "%d %b %H:%M %Y",
                )
            )
        elif "UNTIL PERM" in notam:
            # PERM - permanent reservation
            notam_end = "PERM"
        elif "UNTIL UFN" in notam:
            # UFN (Until Further Notice) - reservation valid
            #  until further notice
            notam_end = "UFN"
        else:
            logger.warning(
                "Error getting the end date of the reservation "
                "from the reservation text."
            )
            notam_end = "N/A"
    except Exception as err:
        raise ParserError(
            "Error getting the end date of the reservation "
            "from the reservation text.\n"
            f"Error: {err}"
        ) from err
    else:
        logger.debug(f"End date: {notam_end}")
        return notam_end


def notam_to_json(
    artcc: str, notam: str, notam_site: str
) -> dict[str, Union[str, datetime.datetime]]:
    """
    Parses the components of a reservation text
    and forms a JSON structure for storing in a database.

    Args:
        artcc (str): The abbreviated ARTCC.
        notam (str): The reservation text.
        notam_site (str): The site associated with the reservation.

    Returns:
        dict[str, Union[str, datetime.datetime]]: A dictionary
          describing the reservation for storing in a database.
    """
    notam_number = get_notam_number(notam)
    logger.debug(f"Forming JSON data structure for reservation {notam_number}")
    notam_create = get_notam_create(notam)
    notam_start = get_notam_start(notam)
    notam_end = get_notam_end(notam)

    # Form the JSON structure for storing in a database
    notam_json = {
        "notam_number": notam_number,  # reservation number
        "notam_artcc": artcc,  # abbreviated ARTCC
        "notam_artcc_full": "",  # full ARTCC data
        # TODO: write a function to get full ARTCC data
        #       from the database"
        "notam_full": notam,  # full reservation text
        "notam_start": notam_start,  # reservation start time
        "notam_end": notam_end,  # reservation end time
        "notam_create": notam_create,  # reservation creation time
        "notam_coordinates": "",  # reservation coordinates
        #  TODO: write a function to extract different coordinates
        "notam_site": notam_site,
    }
    logger.debug(
        f"Completed forming JSON data structure " f"for NOTAM {notam_number}"
    )
    return notam_json
