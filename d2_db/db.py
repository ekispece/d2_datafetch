import pymongo

client = None
client = pymongo.MongoClient("localhost", 27017)


def get_database():
    return client.d2_ml
