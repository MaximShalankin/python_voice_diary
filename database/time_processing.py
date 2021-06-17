import datetime
from typing import Tuple, Union


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


def get_time_interval(end_date: Union[str, int], minutes_delta: int) -> Tuple[int, int]:
    """
    Возвращает интервал из двух дат: начальная (end_date - minutes_back) и конечная (end_date)
    в формате timestamp
    """
    
    if isinstance(end_date, str):
        end_date = int(datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S').timestamp())
        start_date = int((end_date - minutes_delta * 60))
        return start_date, end_date
        
    
    elif isinstance(end_date, int) or isinstance(end_date, float):
        start_date = int((end_date - minutes_delta * 60))
        return start_date, int(end_date)
