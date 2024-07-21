import os
import subprocess
import tempfile

def compile_cpp(code: str):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.cpp', delete=False) as tmp:
        code_file = tmp.name
        tmp.write(code)
    compile_command = ['g++', '-std=c++23', code_file, '-o', os.path.join(base_dir, 'tmp.out')]
    try:
        subprocess.run(compile_command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        return {
            "status": "Compile Error",
            "error_message": e.stderr.strip()
        }