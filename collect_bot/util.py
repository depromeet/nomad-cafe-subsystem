# 이미 수집된 데이터의 경우 제외하고 배열을 재생성
def excloud_exist_data_for_array(src, diff):
    result = []
    for obj in src:
        if obj in diff:
            continue
        result.append(obj)

    return result
