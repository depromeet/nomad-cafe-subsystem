import configparser

import collector
import os
import tqdm
import json


class CollectorFile(collector.Collector):
    def __init__(self, config_map):
        super().__init__(config_map)
        self.total_count = 0
        self.progress_bar = {}

    # 데이터 수집 시작
    def collect(self):
        base_dir = "./data"
        file_list = os.listdir(base_dir)
        self.progress_bar = tqdm.tqdm(total=len(file_list), desc="카페 정보 데이터 저장 중")

        for file_name in file_list:
            self.upsert_db(f"{base_dir}/{file_name}")

    def upsert_db(self, file_path):
        with open(file_path, encoding="utf-8") as json_file:
            try:
                objs = json.load(json_file)
                if not objs:
                    return

                self.db.upsert_many(objs)
                count = len(objs)
                self.total_count += count
                self.progress_bar.update(count)
                print(f"{file_path} collected {count}, total : {self.total_count}")
            except Exception as e:
                print(e)


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('collect_bot.ini')
    config_map = {}
    for key in config.keys():
        config_map[key] = dict(config.items(key))
    CollectorFile(config_map).collect()
