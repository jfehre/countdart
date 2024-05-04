"""Initializes monog client
"""

from pymongo import MongoClient

from countdart.settings import settings

__all__ = {"database"}

client = MongoClient(host=str(settings.MONGO_DB_SERVER), directConnection=True)

database = client[settings.MONGO_DB_DATABASE]


class NotFoundError(ValueError):
    """Not found error to specify errors in mongodb crud operations.
    This allows more specified handling of errors

    Args:
        ValueError (_type_): _description_
    """

    pass


class NameAlreadyTakenError(ValueError):
    """Name already taken error to specifiy errors when creating new documents
    in mongodb

    Args:
        ValueError (_type_): _description_
    """

    pass
