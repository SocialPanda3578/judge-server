import os
import signal
import subprocess
import time
import psutil
import tempfile
from contextlib import contextmanager


# 定义信号处理器来处理超时
@contextmanager
def time_limit(milliseconds):
    def signal_handler(signum, frame):
        raise TimeoutError("Time Limit Exceeded")

    # 设置信号处理器
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(milliseconds // 1000)  # 将毫秒转换为秒
    try:
        yield
    except TimeoutError as e:
        raise e
    finally:
        # 取消信号处理器
        signal.alarm(0)


def check(std_input_content, std_output_content, time_limit_ms, memory_limit_kb):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    run_start_time = time.time()
    run_command = [os.path.join(base_dir, 'tmp.out')]

    # 创建一个临时文件用于保存程序的当前输出
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as cur_output_file:
        # 使用subprocess.PIPE来创建输入输出管道
        proc = subprocess.Popen(run_command, stdin=subprocess.PIPE, stdout=cur_output_file, stderr=subprocess.PIPE)

        # 将标准输入内容写入stdin
        proc.stdin.write(std_input_content.encode())
        proc.stdin.close()

        # 监控内存使用
        memory_usage_kb = 0
        try:
            with time_limit(time_limit_ms):
                while proc.poll() is None:
                    try:
                        mem_info = psutil.Process(proc.pid).memory_info()
                        # 将内存使用量从字节转换为千字节
                        memory_usage_kb = max(memory_usage_kb, mem_info.rss // 1024)
                        if memory_usage_kb > memory_limit_kb:
                            raise MemoryError("MLE")
                    except psutil.NoSuchProcess:
                        break
        except TimeoutError:
            proc.terminate()
            return {
                "status": "TLE",
                "run_time": time_limit_ms / 1000,
                "memory_usage": memory_usage_kb
            }
        except MemoryError:
            proc.terminate()
            return {
                "status": "MLE",
                "run_time": time.time() - run_start_time,
                "memory_usage": memory_usage_kb
            }

        exit_code = proc.wait()  # 等待进程结束
        run_end_time = time.time()

    # 清理临时文件
    cur_output_file_path = cur_output_file.name

    # 读取临时文件的内容
    with open(cur_output_file_path, 'r') as f_cur_output:
        cur_output_data = f_cur_output.read().strip()
    # 比较当前输出文件和标准输出文件内容
    std_output_data = std_output_content.strip()
    cur_output_data = cur_output_data.replace('\r\n', '\n')
    std_output_data = std_output_data.replace('\r\n', '\n')

    if exit_code != 0:
        # RunTimeError
        return {
            "status": "RE",
            "run_time": run_end_time - run_start_time,
            "memory_usage": memory_usage_kb
        }

    if cur_output_data == std_output_data:
        # Accept
        return {
            "status": "AC",
            "run_time": run_end_time - run_start_time,
            "memory_usage": memory_usage_kb
        }
    else:
        # WrongAnswer
        return {
            "status": "WA",
            "run_time": run_end_time - run_start_time,
            "memory_usage": memory_usage_kb
        }
