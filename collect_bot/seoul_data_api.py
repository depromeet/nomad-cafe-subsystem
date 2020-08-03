import configparser
import http_util


class SeoulDataAPI:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('collect_bot.ini')

        if "seoul_data" not in config:
            raise Exception("invalid config (not exit seoul data setting)")

        temp = dict(config.items("seoul_data"))
        config_key_groups = ['url', 'key']
        for key in config_key_groups:
            if key not in temp:
                raise Exception(f"invalid config (not exit {key}")

        self.url = temp["url"]
        self.key = temp["key"]

    def get(self, start, end):
        resp = http_util.HTTPUtil.get(f"{self.url}/{self.key}/json/coffeeShopInfo/{start}/{end}/")
        if "coffeeShopInfo" not in resp:
            raise Exception("not exist key (coffeeShopInfo)")

        if "RESULT" not in resp["coffeeShopInfo"]:
            raise Exception("not exist key (RESULT)")

        if resp["coffeeShopInfo"]["RESULT"]["CODE"] != "INFO-000":
            raise Exception(resp["coffeeShopInfo"]["RESULT"]["MESSAGE"])

        return resp["coffeeShopInfo"]
