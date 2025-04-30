from server import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import subprocess
import json
from main import start_bot
# from database.engine import create_db
from database.crud.filial_crud import get_all_filials, clear_filial_table

app = FastAPI()

# Разрешаем CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await start_bot()

@app.get("/api/ping")
async def ping():
    return {"status": "ok"}


@app.get("/api/del_filials")
async def del_filials():
    await clear_filial_table()
    return {"status": "ok"}


@app.get("/api/data")
async def get_data():
    filials = await get_all_filials()
    result = [filial.dict() for filial in filials]
    return JSONResponse(content=result)

@app.get("/api/run")
async def run_parser():
    try:
        command = ["xvfb-run", "-a", "python3", "run.py"]
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            return {"status": "success", "output": stdout.decode()}
        else:
            raise HTTPException(status_code=500, detail=stderr.decode())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



