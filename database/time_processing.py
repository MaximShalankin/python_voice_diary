import datetime


def timestamp_to_date(timestamp: int) -> str:
    """
    Конвертирует timestamp в читаемый формат даты
    """

    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


def date_to_timestamp(date: str) -> int:
    """
    Конвертирует дату в timestamp
    """

    return int(datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S').timestamp())
