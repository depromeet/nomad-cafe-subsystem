import configparser

import pymongo


class Mongo:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('collect_bot.ini')

        temp = {}
        if "mongo" not in config:
            print("invalid config (not exit mongo db setting)")
            exit(1)

        for (k, v) in config.items("mongo"):
            temp[k] = v

        if "scheme" not in temp:
            print("invalid config (not exit scheme)")
            exit(1)

        if "host" not in temp:
            print("invalid config (not exit host)")
            exit(1)

        if "port" not in temp:
            print("invalid config (not exit port)")
            exit(1)

        if "dbname" not in temp:
            print("invalid config (not exit dbname)")
            exit(1)

        if "collection" not in temp:
            print("invalid config (not exit collection)")
            exit(1)

        if "username" not in temp:
            print("invalid config (not exit username)")
            exit(1)

        if "password" not in temp:
            print("invalid config (not exit password)")
            exit(1)

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

    def insert_one(self, data):
        self.db.insert_one(data)

    def find(self, filters=None):
        if filters is None:
            filters = {}
        return self.db.find(filters)


if __name__ == '__main__':
    db = Mongo()
    db.insert_one({"name": "sample"})
    print(db.find())
