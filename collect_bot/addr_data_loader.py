import json

import openpyxl
import shapefile


def load_seoul_towns():
    # 엑셀파일 열기
    wb = openpyxl.load_workbook('national_division.xlsx')
    ws = wb.get_sheet_by_name("2013년")

    towns = []
    for r in ws.rows:
        if r[0].row < 3:  # 1 ~ 2번 라인은 헤더
            continue
        city_code = r[0].value  # 시도코드
        city_name = r[1].value  # 시도명칭
        district_code = r[2].value  # 시군구코드
        district_name = r[3].value  # 시군구명칭
        town_code = r[4].value  # 읍면동코드
        town_name = r[5].value  # 읍면동명칭

        if city_name != "서울특별시":
            continue

        towns.append(town_name)
        print(city_code, city_name, district_code, district_name, town_code, town_name)

    wb.close()
    return towns


def load_seoul_villages():
    r = shapefile.Reader("LI.shp", encoding="cp949")
    return r.records()


def load_national_divisions():
    divisions = []
    with open('national_division.json') as json_file:
        obj = json.load(json_file)
        if not obj:
            raise Exception("not exist seoul division data")

        if not obj["features"]:
            raise Exception("not exist seoul division features")

        for feature in obj["features"]:
            if not feature["properties"]:
                continue
            if not feature["properties"]["name"]:
                continue
            divisions.append(feature['properties']['name'])

    return divisions
