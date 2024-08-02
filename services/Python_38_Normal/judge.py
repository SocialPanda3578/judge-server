import os
import tempfile

from minio import Minio

from services.python38_normal import check
from minio.error import S3Error


def judge_python(code: str, pid: str, client: Minio):
    max_run_time = 0
    max_memory_usage = 0
    testcase_count = 0
    re_count = mle_count = tle_count = wa_count = ac_count = 0
    final_status = 'judging'
    result_queue = ''
    message = 'null'
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
        tmp.write(code)
        runner_path = tmp.name

    try:
        # minio
        try:
            objects = client.list_objects('problems', prefix='/P/' + pid + '/IN', recursive=True)
            for obj in objects:  # 遍历 { 测试点文件夹 }/IN
                std_input_file = std_output_file = obj.object_name
                std_output_file = std_output_file.replace('input', 'output')
                std_output_file = std_output_file.replace('IN', 'OUT')  # 测试点文件名处理
                data = client.get_object('problems', std_input_file)
                std_input_file_data = data.read().decode('utf-8')  # 读取标准输入内容
                data = client.get_object('problems', std_output_file)
                std_output_file_data = data.read().decode('utf-8')  # 读取标准输出内容
                result = check.check(runner_path, std_input_file_data, std_output_file_data, 1000, 10000000)  # 提交测试
                testcase_count = testcase_count + 1  # 测试点计数器+1
                max_run_time = max(max_run_time, result['run_time'])  # 计算最大运行时间
                max_memory_usage = max(max_memory_usage, result['memory_usage'])  # 计算最大内存占用
                # 答案错误
                if result['status'] == 'WA':
                    result_queue += 'W'
                    wa_count += 1
                # 运行超时
                if result['status'] == 'TLE':
                    result_queue += 'T'
                    tle_count += 1
                # 内存超限
                if result['status'] == 'MLE':
                    result_queue += 'M'
                    mle_count += 1
                # 运行时错误
                if result['status'] == 'RE':
                    result_queue += 'R'
                    re_count += 1
                # 答案正确
                if result['status'] == 'AC':
                    result_queue += 'A'
                    ac_count += 1
        except S3Error as err:
            # minio错误
            final_status = 'Minio Error'
            message = str(err)
    except Exception as err:
        # 服务器错误
        final_status = 'Server Error'
        message = str(err)

    # 判断最终返回值
    os.remove(runner_path)
    if testcase_count == 0:
        final_status = 'Judge Error'
    if final_status == 'judging':
        if re_count > 0: final_status = 'Runtime Error'
        elif wa_count > 0: final_status = 'Wrong Answer'
        elif tle_count > 0: final_status = 'Time Limit Exceeded'
        elif mle_count > 0: final_status = 'Memory Limit Exceeded'
        elif ac_count == testcase_count: final_status = 'Accept'
        else: final_status = 'Server Error'
    return {
        "status": final_status,
        "max_run_time": max_run_time,
        "max_memory_usage": max_memory_usage,
        "message": message,
        "testcase_count": testcase_count,
        "result_queue": result_queue
    }
