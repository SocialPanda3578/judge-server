import os
import tempfile
from services.python import check_python
from minio import Minio
from minio.error import S3Error


def judge_python(code: str, pid: str):
    max_run_time = 0
    max_memory_usage = 0
    testcase_count = 0
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
        tmp.write(code)
        runner_path = tmp.name
    # minio
    client = Minio(
        '127.0.0.1:9000',  # MinIO服务器的URL
        access_key='minioadmin',  # MinIO访问密钥
        secret_key='minioadmin',  # MinIO秘密密钥
        secure=False  # 如果是HTTPS连接设置为True
    )
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
                result = check_python.check(runner_path, std_input_file_data, std_output_file_data, 1000, 10000000)  # 提交测试
                testcase_count = testcase_count + 1  # 测试点计数器+1
                max_run_time = max(max_run_time, result['run_time'])  # 计算最大运行时间
                max_memory_usage = max(max_memory_usage, result['memory_usage'])  # 计算最大内存占用
                if result['status'] == 'WA':  # 答案错误
                    return {
                        "status": "Wrong Answer",
                        "max_run_time": max_run_time,
                        "max_memory_usage": max_memory_usage,
                        "message": 'none'
                    }
                if result['status'] == 'TLE':  # 运行超时
                    print('TLE')
                    return {
                        "status": "Time Limit Exceeded",
                        "max_run_time": max_run_time,
                        "max_memory_usage": max_memory_usage,
                        "message": 'none'
                    }
                if result['status'] == 'MLE':  # 内存超限
                    return {
                        "status": "Memory Limit Exceeded",
                        "max_run_time": max_run_time,
                        "max_memory_usage": max_memory_usage,
                        "message": 'none'
                    }
                if result['status'] == 'AC':  # 答案正确
                    return {
                        "status": "Accept",
                        "max_run_time": max_run_time,
                        "max_memory_usage": max_memory_usage,
                        "message": 'none'
                    }
        except S3Error as err:
            print(err)
        return {
            "status": "Runtime Error",  # 运行时错误
            "max_run_time": max_run_time,
            "max_memory_usage": max_memory_usage,
            "message": 'none'
        }
    except Exception as e:
        return {
            "status": "Server Error",  # 服务器错误
            "message": str(e)
        }
