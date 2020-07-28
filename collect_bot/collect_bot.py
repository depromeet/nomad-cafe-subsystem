import configparser
import json

import requests


class CollectBot:
    """
    지역별 카페 정보를 수집하는 봇
    """

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('collect_bot.ini')

        self.bot = {}
        if "bot" not in config:
            print("invalid config (not exit bot setting)")
            exit(1)

        for (k, v) in config.items("bot"):
            self.bot[k] = v

        if "api_type" not in self.bot:
            print("invalid config (not exit api setting)")
            exit(1)

        if self.bot["api_type"] == "naver":
            self.api = NaverAPI()
        elif self.bot["api_type"] == "seoul_data":
            self.api = {}
        else:
            print("invalid api type.", self.bot["api_type"])
            exit(1)

        self.sample_query()

    def sample_query(self):
        self.api.get('카페', 1)


class HTTPUtil:
    def __init__(self):
        print('')

    @staticmethod
    def get(url, params, headers):
        resp = requests.get(url=url, params=params, headers=headers)
        resp_json = json.loads(resp.text)
        print(json.dumps(resp_json, indent=4, sort_keys=True))
        return resp_json

    @staticmethod
    def post(url, data):
        resp = requests.post(url=url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
        resp_json = json.loads(resp.text)
        print(json.dumps(resp_json, indent=4, sort_keys=True))
        return resp_json


class NaverAPI:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('collect_bot.ini')

        temp = {}
        if "naver" not in config:
            print("invalid config (not exit naver api setting)")
            exit(1)

        for (k, v) in config.items("naver"):
            temp[k] = v

        if "url" not in temp:
            print("invalid config (not exit url)")
            exit(1)

        if "client_id" not in temp:
            print("invalid config (not exit client id)")
            exit(1)

        if "client_secret" not in temp:
            print("invalid config (not exit client secret)")
            exit(1)

        self.url = temp["url"]
        self.client_id = temp["client_id"]
        self.client_secret = temp["client_secret"]

    def get(self, query, start):
        params = {
            'query': query.encode("utf-8"),
            'display': 5,  # max=5
            'start': start,  # 검색 시작 포인트
            'sort': 'random'  # random 일 경우 유사도순
        }

        HTTPUtil.get(self.url, params=params, headers={
            'X-Naver-Client-Id': self.client_id,
            'X-Naver-Client-Secret': self.client_secret,
        })


CollectBot()
