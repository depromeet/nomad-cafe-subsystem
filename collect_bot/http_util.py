import json

import requests


class HTTPUtil:
    def __init__(self):
        print('')

    @staticmethod
    def get(url, params, headers):
        resp = requests.get(url=url, params=params, headers=headers)
        resp_json = json.loads(resp.text)
        print(json.dumps(resp_json, indent=4, sort_keys=True, ensure_ascii=False))
        return resp_json

    @staticmethod
    def post(url, data):
        resp = requests.post(url=url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
        resp_json = json.loads(resp.text)
        print(json.dumps(resp_json, indent=4, sort_keys=True, ensure_ascii=False))
        return resp_json
