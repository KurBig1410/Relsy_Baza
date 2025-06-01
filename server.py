from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import subprocess
import json
from main import start_bot
from fastapi import Query
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from fastapi.encoders import jsonable_encoder

# from database.engine import create_db
from database.crud.filial_crud import (
    get_aggregated_filials,
    get_aggregated_stats,
    get_all_filials,
    clear_filial_table,
    get_filials_in_range,
)

# from migrate_sqlite_to_postgres import migrate_sqlite_to_postgres

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
    print("🚀 FastAPI стартует")
    asyncio.create_task(start_bot())
    print("🤖 Бот запущен в фоне")


@app.get("/api/ping")
async def ping():
    return {"status": "ok"}


# @app.get("/api/migrate")
# async def migrate():
#     migrate_sqlite_to_postgres()
#     return {"status": "ok"}


@app.get("/api/del_filials")
async def del_filials():
    await clear_filial_table()
    return {"status": "ok"}


# @app.get("/api/data")
# async def get_data():
#     filials = await get_all_filials()
#     result = [filial.dict() for filial in filials]
#     return JSONResponse(content=result)


# @app.get("/api/data")
# async def get_data(
#     start: datetime = Query(default=None), end: datetime = Query(default=None)
# ):
#     filials = await get_filials_in_range(start_date=start, end_date=end)
#     return JSONResponse(content=[f.dict() for f in filials])


# @app.get("/api/data")
# async def get_data(start: datetime = Query(default=None), end: datetime = Query(default=None)):
#     filials = await get_filials_in_range(start_date=start, end_date=end)
#     return JSONResponse(content=jsonable_encoder(filials))


@app.get("/api/data")
async def get_data(start: datetime = Query(default=None), end: datetime = Query(default=None)):
    if not start or not end:
        end = datetime.today()
        start = end - timedelta(days=29)

    rows = await get_aggregated_filials(start, end)

    result = [
        {
            "name": r[0],
            "owner": r[1],
            "income": r[2],
            "service_sum": r[3],
            "goods_sum": r[4],
            "avg_check_total": r[5],
            "avg_check_service": r[6],
            "avg_filling": r[7],
            "new_clients": r[8],
            "repeat_clients": r[9],
            "lost_clients": r[10],
            "total_appointments": r[11],
            "canceled_appointments": r[12],
            "finished_appointments": r[13],
            "unfinished_appointments": r[14],
            "population_category": r[15],
        }
        for r in rows
    ]

    return JSONResponse(content=jsonable_encoder(result))


@app.get("/api/stats")
async def get_stats(
    start: datetime = Query(default=None), end: datetime = Query(default=None)
):
    if not start or not end:
        end = datetime.today()
        start = end - timedelta(days=29)

    income, service_sum, avg_check, count = await get_aggregated_stats(start, end)

    return JSONResponse(
        content={
            "from": start.strftime("%Y-%m-%d"),
            "to": end.strftime("%Y-%m-%d"),
            "income_sum": income,
            "service_sum": service_sum,
            "avg_check": avg_check,
            "days_count": count,
        }
    )


@app.get("/api/run")
async def run_parser():
    try:
        command = ["xvfb-run", "-a", "python3", "run.py"]
        process = await asyncio.create_subprocess_exec(
            *command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            return {"status": "success", "output": stdout.decode()}
        else:
            raise HTTPException(status_code=500, detail=stderr.decode())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
