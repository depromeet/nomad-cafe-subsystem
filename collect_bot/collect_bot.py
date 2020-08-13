import configparser

import collector_naver
import collector_seoul_data
import collector_daum


class CollectBot:
    """
    지역별 카페 정보를 수집하는 봇
    """

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('collect_bot.ini')
        config_map = {}
        for key in config.keys():
            config_map[key] = dict(config.items(key))

        if "bot" not in config_map:
            raise Exception("invalid config (not exit bot setting)")

        config_key_groups = ['api_type', 'db_type']
        for key in config_key_groups:
            if key not in config_map["bot"]:
                raise Exception(f"invalid config (not exit {key}")

        if config_map["bot"]["api_type"] == "naver":
            self.collector = collector_naver.CollectorForNaver(config_map)
        elif config_map["bot"]["api_type"] == "seoul-data":
            self.collector = collector_seoul_data.CollectorForSeoulData(config_map)
        elif config_map["bot"]["api_type"] == "daum":
            self.collector = collector_daum.CollectorForDaum(config_map)
        else:
            raise Exception("invalid api type.", config_map["bot"]["api_type"])

    def collect(self):
        self.collector.collect()


if __name__ == '__main__':
    bot = CollectBot()
    bot.collect()
