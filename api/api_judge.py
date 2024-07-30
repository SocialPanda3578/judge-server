from fastapi import APIRouter
from pydantic import BaseModel
from services.cpp import judge_cpp

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

    if language == "cpp":
        res = judge_cpp.judge_cpp(code, 'P1000')
    if language == "python":
        res = judge_python.judge_python(code,'P1000')
    if language == "java":
        res = judge_java.judge_java(code,'P1000')
    return {'status': 'OK', 'result': res}