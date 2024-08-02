import os
import tempfile

from fastapi import APIRouter
from minio import Minio
from pydantic import BaseModel
from services.cpp import judge_cpp
from services.java import judge_java
from services.python import judge_python

api_judge = APIRouter()
# minio
client = Minio(
    '127.0.0.1:9000',  # MinIO服务器的URL
    access_key='minioadmin',  # MinIO访问密钥
    secret_key='minioadmin',  # MinIO秘密密钥
    secure=False  # 如果是HTTPS连接设置为True
)

class CodeEvaluationRequest(BaseModel):
    code: str
    language: str
    pid: str


@api_judge.post('/judge')
async def judge(request: CodeEvaluationRequest):
    code = request.code
    language = request.language
    pid = request.pid
    res = 'Not Support Language'
    if language == "cpp":
        res = judge_cpp.judge_cpp(code, pid, client)
    if language == "python":
        res = judge_python.judge_python(code, pid, client)
    if language == "java":
        res = judge_java.judge_java(code, pid, client)
    return {'status': 'OK', 'result': res}
