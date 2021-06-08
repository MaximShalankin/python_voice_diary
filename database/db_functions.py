from typing import List
import datetime
from pymongo.errors import DuplicateKeyError
from pymongo.collection import Collection


def add_value(database: Collection, value: str):
    """
    Добавить одну запись в базу данных
    """

    database_index = int(datetime.datetime.now().timestamp())
    try:
        database.insert_one({'_id': database_index, 'text': value})
        return True

    except DuplicateKeyError:
        return False


def del_value(database: Collection, index: int, index_end: int = None):
    """
    Удалить одну или несколько записей по индексу
    """

    if index_end is None:
        database.delete_one(
            {
                "_id": {
                    "$gte": index,
                    "$lt": index + 1
                }
            }
        )

    else:
        database.delete_many(
            {
                "_id": {
                    "$gte": index,
                    "$lt": index_end + 1
                }
            }
        )

    return True


def find_value(database: Collection, index: int, index_end: int = None) -> List:
    """
    Получить одну или несколько записей по индексу
    """
    return [
        value for value in database.find(
            {
                "_id": {
                    "$gte": index,
                    "$lt": index + 1 if index_end is None else index_end + 1
                }
            }
        )
    ]


def find_last_values(database: Collection, last_n_values: int = 5) -> List:
    """
    Получить последние N записей
    """
    return [value for value in database.find().limit(last_n_values).sort([('$natural', -1)])]
