import pymongo

client = pymongo.MongoClient("localhost", 27017)
DIARY_DB = client.database.diary


__all__ = [
    'DIARY_DB',
]
