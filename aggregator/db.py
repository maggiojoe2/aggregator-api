"""Database Helpers."""
from pymongo.mongo_client import MongoClient
from pymongo import errors
from pymongo.cursor import Cursor
from bson.objectid import ObjectId
from typing import Dict, List, Union


async def connect_to_mongo() -> MongoClient:
    """Connect to MongoDB.

    Returns:
        client(MongoClient) : MongoDB client

    """
    client: MongoClient = MongoClient(
        'mongodb://mongodb:27017/', username="admin", password='pass', authSource="admin")
    return client


async def disconnect_mongo(client: MongoClient):
    """Close the MongoDB connection.

    Arguments:
        client(MongoClient) : MongoDB client
    """
    try:
        client.close()
    except errors.PyMongoError:
        raise errors.PyMongoError
    except Exception:
        raise Exception

    return


async def retrieve_objects_from_db(query: dict, database: str, collection: str,
                                   find_one: bool) -> Union[Cursor, Dict[str, object]]:
    """Retrieve email based on email_id.

    Arguments:
        email_id (ObjectId) : ObjectId of the email
        database(str) : Name of the database to be connected
        collection(str) : Name of the collection of database
        find_one(bool) : True if 'find_one' query needs to be executed, False for 'find' query

    Returns:
        Dict if find_one is True
        Cursor if find_one is False

    """
    client: MongoClient = await connect_to_mongo()
    email_object: Union[Dict[str, object], Cursor]
    if find_one:
        email_object = client[database][collection].find_one(query)
    else:
        email_object = client[database][collection].find(query).sort({'time_received': -1})
    if not email_object:
        return {}
    await disconnect_mongo(client)
    return email_object


async def retrieve_count_from_db(query: dict, database: str, collection: str) -> int:
    """Retrieve a count from the db based on query passed.

    Arguments:
        query(List[Dict[str, Union[str, int, None]]]): Query to be sent to db.
        database(str) : Name of the database to be connected
        collection(str) : Name of the collection of database

    Returns:
        int which is the count of the query specified.

    """
    client: MongoClient = await connect_to_mongo()
    cursor = client[database][collection].find(query)
    cursor_count = cursor.count()
    await disconnect_mongo(client)
    return cursor_count


async def mongo_store_info(email: Dict[str, object], client: MongoClient, database: str, collection: str) -> ObjectId:
    """Store email to database.

    Args:
        email(dict) : Dictionary containing email attributes
        client(MongoClient) : MongoDB client
        database(str) : Name of the database to be connected
        collection(str) : Name of the collection of database

    Returns:
        object_id(ObjectId) : MongoDB ObjectID created when document is inserted.

    """
    try:
        db: MongoClient = client[database][collection]
        object_id: ObjectId = db.insert(email)
    except errors.PyMongoError:
        raise errors.PyMongoError
    except Exception:
        raise Exception

    return object_id


async def save_to_db(received_json: Dict[str, object]) -> ObjectId:
    """Connect to db and calls function to store email to db.

    Args:
        received_json(dict) : Dictionary containing email attributes

    Returns:
        object_id(ObjectId) : MongoDB ObjectID created when document is inserted.

    """
    try:
        client: MongoClient = await connect_to_mongo()
        object_id: ObjectId = await mongo_store_info(received_json, client, database='email_db',
                                                     collection='email_collection')
        await disconnect_mongo(client)

    except errors.PyMongoError:
        raise errors.PyMongoError
    except Exception:
        raise Exception

    return object_id


async def update_fields(info_for_query: List[Dict[str, Union[str, int, None]]], object_id: ObjectId,
                        database: str, collection: str):
    """Update field with field_value in specified document, database and collection.

    Arguments:
        info_for_query(List[Dict]) : A list of dictionaries containing field, field_value,
                                     and operation in order to build the db query
        object_id(ObjectID) : '_id' of the object to be updated
        database(str) : Name of the database to be connected
        collection(str) : Name of the collection of database

    Optional Arguments:
        operation(str) : MongoDB operation to be executed on field
    """
    client: MongoClient = await connect_to_mongo()
    try:
        for query in info_for_query:
            client[database][collection].update_one({"_id": object_id},
                                                    {query["operation"]: {
                                                        query["field"]: query["field_value"]}},
                                                    upsert=False)

    except errors.PyMongoError:
        raise errors.PyMongoError
    except Exception:
        raise Exception

    await disconnect_mongo(client)
    return
