from fastapi import FastAPI
import asyncio
import time

app = FastAPI()

@app.get("/slow-async")
async def slow_async():
    await asyncio.sleep(3)

    return {
        "type": "async",
        "message": "3초 대기 완료"
    }

@app.get('/slow-block')
async def slow_block():
    # sync 방식의 대기시간 측정
    time.sleep(3)
    return {"type": "block",
    "message": "3초 대기 완료"}