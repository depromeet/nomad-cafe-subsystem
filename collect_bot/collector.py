from dataclasses import dataclass
import db


@dataclass
class Collector:
    collect_count: int = 0

    def __init__(self, config_map):
        self.config_map = config_map
        if self.config_map["bot"]["db_type"] == "mongo":
            self.db = db.Mongo()
        else:
            raise Exception("invalid db type.", self.config_map["bot"]["db_type"])

    def collect(self, start, end=0):
        pass

    def upsert_many(self, objs):
        self.db.upsert_many(objs)
        self.collect_count += objs.__len__()
        # print(f"current count : {self.collect_count}")
