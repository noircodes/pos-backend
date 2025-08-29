from mongodb.mongo_client import MGDB
from mongodb.mongo_collection_name import CollectionNames
from utils.util_mongodb import TMongoCollection

tb_user: TMongoCollection = MGDB.get_collection(CollectionNames.tb_user.value)