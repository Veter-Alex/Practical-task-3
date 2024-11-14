# создаем класс исключений
class ParserError(Exception):
    """
    Все ошибки парсинга данных.
    """

    pass


class DBError(Exception):
    """
    Все ошибки связанные с операциями с БД.
    """

    pass


class NetworkError(Exception):
    """
    Все ошибки связанные с проблемой в соединения.
    """

    pass


class FileError(Exception):
    """
    Все ошибки связанные с файловыми операциями.
    """

    pass
