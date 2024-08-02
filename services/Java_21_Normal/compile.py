import os
import subprocess
import tempfile


def compile_java(code: str):

    code_file = 'Main.java'
    with open(code_file, 'w') as tmp:
        tmp.write(code)

    try:
        compile_command = ['javac', code_file]
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