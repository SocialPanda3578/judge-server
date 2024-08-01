from fastapi import APIRouter
from pydantic import BaseModel
from services.cpp import judge_cpp
from services.python import judge_python

api_judge = APIRouter()


class CodeEvaluationRequest(BaseModel):
    code: str
    language: str
    pid: str


@api_judge.post('/judge')
async def judge(request: CodeEvaluationRequest):
    code = request.code
    language = request.language
    pid = request.pid
    res = 'ERROR'
    if language == "cpp":
        res = judge_cpp.judge_cpp(code, pid)
    if language == "python":
        res = judge_python.judge_python(code, pid)
    return {'status': 'OK', 'result': res}
