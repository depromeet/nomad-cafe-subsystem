import configparser

import pymongo


class Mongo:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('collect_bot.ini')

        if "mongo" not in config:
            raise Exception("invalid config (not exit mongo db setting)")

        temp = dict(config.items("mongo"))
        config_key_groups = ['scheme', 'host', 'port', 'dbname', 'collection', 'username', 'password']
        for key in config_key_groups:
            if key not in temp:
                raise Exception(f"invalid config (not exit {key}")

        self.scheme = temp["scheme"]
        self.host = temp["host"]
        self.port = temp["port"]
        self.dbname = temp["dbname"]
        self.collection = temp["collection"]
        self.username = temp["username"]
        self.password = temp["password"]

        connect_string = f"{self.scheme}://{self.username}:{self.password}@{self.host}/{self.dbname}?retryWrites" \
                         f"=true&w=majority"
        conn = pymongo.MongoClient(connect_string)
        database = conn.get_database(self.dbname)
        self.db = database.get_collection(self.collection)

    def upsert_one(self, data):
        _id = data.pop("_id")
        self.db.update_one({"_id": _id}, {'$set': data}, upsert=True)

    def upsert_many(self, datas):
        ids = [data.pop("_id") for data in datas]
        operations = [pymongo.UpdateOne({"_id": idn}, {'$set': data}, upsert=True) for idn, data in zip(ids, datas)]
        self.db.bulk_write(operations)

    def find(self, filters=None):
        if not filters:
            filters = {}
        return self.db.find(filters)


if __name__ == '__main__':
    db = Mongo()
    db.upsert_one({"_id": "sample", "name": "sample"})
    print(db.find())
