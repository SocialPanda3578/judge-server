import os
from services import compile_cpp,test_cpp
from minio import Minio
from minio.error import S3Error

def judge_cpp(code: str, pid: str):
    max_run_time=0
    max_memory_usage=0
    testcase_count=0
#compile
    compile_cpp.compile_cpp(code)
#minio
    client = Minio(
        '127.0.0.1:9000',  # MinIO服务器的URL
        access_key='minioadmin',  # MinIO访问密钥
        secret_key='minioadmin',  # MinIO秘密密钥
        secure=False  # 如果是HTTPS连接设置为True
    )

    try:
#minio
        try:
            objects = client.list_objects('problems', prefix='/P/P1000/IN', recursive=True)
            for obj in objects:
                std_input_file = obj.object_name
                std_output_file = obj.object_name
                std_output_file = std_output_file.replace('input', 'output')
                std_output_file = std_output_file.replace('IN' , 'OUT')
                data = client.get_object('problems', std_input_file)
                std_input_file_data = data.read().decode('utf-8')
                data = client.get_object('problems', std_output_file)
                std_output_file_data = data.read().decode('utf-8')
                result=test_cpp.test(std_input_file_data, std_output_file_data,1000,10000000)
                testcase_count = testcase_count + 1
                max_run_time = max(max_run_time,result['run_time'])
                max_memory_usage = max(max_memory_usage,result['memory_usage'])
                if(result['status'])=='WA':
                    return {
                        "status": "Wrong Answer",
                        "max_run_time": max_run_time,
                        "max_memory_usage": max_memory_usage
                    }
                if(result['status']=='TLE'):
                    print('TLE')
                    return {
                        "status": "Time Limit Exceeded",
                        "max_run_time": max_run_time,
                        "max_memory_usage": max_memory_usage
                    }
                if(result['status']=='MLE'):
                    return {
                        "status": "Memory Limit Exceeded",
                        "max_run_time": max_run_time,
                        "max_memory_usage": max_memory_usage
                    }
        except S3Error as err:
            print(err)
        return {
            "status": "Accept",
            "max_run_time": max_run_time,
            "max_memory_usage": max_memory_usage
        }
    except Exception as e:
        return {
            "status": "Server Error",
            "error_message": str(e)
        }