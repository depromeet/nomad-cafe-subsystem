import concurrent.futures
from concurrent.futures import ThreadPoolExecutor


class Runner:
    # 실행할 함수, 함수에 전달할 인자, 병렬 실행 수를 받아 병렬 실행
    def run(self, run_func, arg, parallel_count=8):
        split_arrs = self.split_array_per_count(arg, parallel_count)

        thread_list = []
        with ThreadPoolExecutor(max_workers=parallel_count) as executor:
            for arr in split_arrs:
                thread_list.append(executor.submit(run_func, arr))

            for execution in concurrent.futures.as_completed(thread_list):
                execution.result()

    # 실행할 함수, 함수에 전달할 인자, 병렬 실행 수를 받아 병렬 실행
    def run_dict(self, run_func, arg, parallel_count=8):
        split_dicts = self.split_dict_per_count(arg, parallel_count)

        thread_list = []
        with ThreadPoolExecutor(max_workers=parallel_count) as executor:
            for key, value in split_dicts:
                thread_list.append(executor.submit(run_func, arr))

            for execution in concurrent.futures.as_completed(thread_list):
                execution.result()

    # 병렬 실행을 위해 인자로 전달된 수만큼 배열을 쪼갬
    @staticmethod
    def split_array_per_count(src_arr, count):
        result_arr = []
        for i in range(count):
            result_arr.append([])

        count_per_arr = len(src_arr) / count
        idx = 0
        currl_count = 0
        for obj in src_arr:
            result_arr[idx].append(obj)
            if currl_count > count_per_arr:
                idx += 1
                currl_count = 0
                continue

            currl_count += 1

        print(f"count per arr : {int(count_per_arr)}, split : {len(result_arr)}")
        for obj in result_arr:
            print(f"split count : {len(obj)}, data : {obj}")
        return result_arr

    # 병렬 실행을 위해 인자로 전달된 수만큼 배열을 쪼갬
    def split_dict_per_count(self, src_dict, count):
        src_arr = []
        for key in src_dict.keys():
            src_arr.extend(src_dict[key])

        return self.split_array_per_count(src_arr, count)
