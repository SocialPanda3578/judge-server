import os
import subprocess
import tempfile


def compile_java(code: str):
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # 使用固定的临时文件名 'runner.java'，用于存放Java源代码
    code_file = 'Main.java'

    # 写入Java源代码到临时文件
    with open(code_file, 'w') as tmp:
        tmp.write(code)

    try:
        # 编译Java源代码，输出到base_dir
        compile_command = ['javac', code_file, '-d', base_dir]
        subprocess.run(compile_command, check=True, capture_output=True, text=True)


        # 清理临时源文件
        os.remove(code_file)
        return {
            "status": "OK",
            "message": "null"
        }
    except subprocess.CalledProcessError as e:
        # 如果编译失败，返回编译错误信息
        return {
            "status": "CE",
            "message": e.stderr.strip()
        }