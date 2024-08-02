from services.cpp import check_cpp, compile_cpp
from minio import Minio
from minio.error import S3Error


def judge_cpp(code: str, pid: str):
    max_run_time = 0
    max_memory_usage = 0
    testcase_count = 0
    final_status = 'judging'
    result_queue = ''
    # compile
    compile_result = compile_cpp.compile_cpp(code)  # 提交编译
    message = compile_result['message'],
    if compile_result['status'] == 'CE':  # 编译错误
        return {
            "status": "Compile Error",
            "max_run_time": max_run_time,
            "max_memory_usage": max_memory_usage,
            "message": message,
            "testcase_count": testcase_count,
            "result_queue": result_queue
        }
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
                result = check_cpp.check(std_input_file_data, std_output_file_data, 1000, 10000000)  # 提交测试
                testcase_count = testcase_count + 1  # 测试点计数器+1
                max_run_time = max(max_run_time, result['run_time'])  # 计算最大运行时间
                max_memory_usage = max(max_memory_usage, result['memory_usage'])  # 计算最大内存占用
                # 答案错误
                if result['status'] == 'WA':
                    result_queue += 'W'
                    if final_status == 'judging':
                        final_status = 'Wrong Answer'
                # 运行超时
                if result['status'] == 'TLE':
                    result_queue += 'T'
                    if final_status == 'judging':
                        final_status = 'Time Limit Exceeded'
                # 内存超限
                if result['status'] == 'MLE':
                    result_queue += 'M'
                    if final_status == 'judging':
                        final_status = 'Memory Limit Exceeded'
                # 运行时错误
                if result['status'] == 'RE':
                    result_queue += 'R'
                    if final_status == 'judging':
                        final_status = 'Runtime Error'
                # 答案正确
                if result['status'] == 'AC':
                    result_queue += 'A'
        except S3Error as err:
            # minio错误
            final_status = 'Minio Error'
            message = str(err)
    except Exception as err:
        # 服务器错误
        final_status = 'Server Error'
        message = str(err)

    # 判断最终返回值
    if final_status == 'judging':
        final_status = 'Accept'
    return {
        "status": final_status,
        "max_run_time": max_run_time,
        "max_memory_usage": max_memory_usage,
        "message": message,
        "testcase_count": testcase_count,
        "result_queue": result_queue
    }
