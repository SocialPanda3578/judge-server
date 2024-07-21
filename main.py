from fastapi import FastAPI
import uvicorn
from api.api_judge import api_judge
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头部
)

app.include_router(api_judge, prefix="/services", tags=["services API"])

@app.get("/check" , tags=["check API"])
async def check():
    return {"isOnline": "true"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)