# crud/filial_crud.py
from sqlmodel import select, delete
from database.filial import Filial
from datetime import datetime, timedelta
from database.engine import session_maker
from sqlmodel import func


async_session = session_maker


async def create_filial(filial: Filial):
    async with async_session() as session:
        async with session.begin():
            session.add(filial)
        await session.refresh(filial)
        return filial


async def get_filial_by_id(filial_id: int):
    async with async_session() as session:
        result = await session.exec(select(Filial).where(Filial.id == filial_id))
        return result.first()


async def get_filials_by_city(city_name: str):
    async with async_session() as session:
        result = await session.exec(
            select(Filial).where(Filial.name.contains(city_name))
        )
        return result.all()


async def get_filials_by_owner(owner_name: str):
    async with async_session() as session:
        result = await session.exec(select(Filial).where(Filial.owner == owner_name))
        return result.all()


async def delete_filial_by_id(filial_id: int):
    async with async_session() as session:
        async with session.begin():
            result = await session.exec(select(Filial).where(Filial.id == filial_id))
            filial = result.first()
            if filial:
                await session.delete(filial)
                return True
            return False


async def delete_filial_by_name(filial_name: str):
    async with async_session() as session:
        async with session.begin():
            result = await session.exec(
                select(Filial).where(Filial.name == filial_name)
            )
            filial = result.first()
            if filial:
                await session.delete(filial)
                return True
            return False


async def delete_filials_by_owner(owner_name: str):
    async with async_session() as session:
        async with session.begin():
            result = await session.exec(
                select(Filial).where(Filial.owner == owner_name)
            )
            filials = result.all()
            for filial in filials:
                await session.delete(filial)
            return len(filials)


async def get_all_filials():
    async with async_session() as session:
        result = await session.exec(select(Filial))
        filials = result.all()
        for filial in filials:
            print(f"\n\n\n{filial.dict()}\n\n\n")
        return filials


async def get_filials_in_range(start_date: datetime = None, end_date: datetime = None):
    if not start_date:
        end_date = datetime.today()
        start_date = end_date - timedelta(days=29)

    async with async_session() as session:
        result = await session.exec(
            select(Filial).where(
                Filial.report_date >= start_date,
                Filial.report_date <= end_date
            )
        )
        return result.all()
    

# db.py или crud.py
async def get_aggregated_stats(start_date: datetime, end_date: datetime):
    async with async_session() as session:
        result = await session.exec(
            select(
                func.sum(Filial.income),
                func.sum(Filial.service_sum),
                func.avg(Filial.avg_check_total),
                func.count()
            ).where(
                Filial.report_date >= start_date,
                Filial.report_date <= end_date
            )
        )
        return result.one()


async def get_filial_by_name(session, name: str):
    result = await session.exec(select(Filial).where(Filial.name == name))
    return result.first()


async def clear_filial_table():
    async with async_session() as session:
        async with session.begin():
            await session.exec(delete(Filial))
        print("✅ Таблица filial очищена.")



async def get_aggregated_filials(start_date: datetime, end_date: datetime):
    async with async_session() as session:
        result = await session.exec(
            select(
                Filial.name,
                Filial.owner,
                func.sum(Filial.income).label("income"),
                func.sum(Filial.service_sum).label("service_sum"),
                func.sum(Filial.goods_sum).label("goods_sum"),
                func.sum(Filial.avg_check_total).label("avg_check_total"),  # сумма среднего чека — так же
                func.sum(Filial.avg_check_service).label("avg_check_service"),
                func.sum(Filial.avg_filling).label("avg_filling"),
                func.sum(Filial.new_clients).label("new_clients"),
                func.sum(Filial.repeat_clients).label("repeat_clients"),
                func.sum(Filial.lost_clients).label("lost_clients"),
                func.sum(Filial.total_appointments).label("total_appointments"),
                func.sum(Filial.canceled_appointments).label("canceled_appointments"),
                func.sum(Filial.finished_appointments).label("finished_appointments"),
                func.sum(Filial.unfinished_appointments).label("unfinished_appointments"),
                func.max(Filial.population_category).label("population_category"),  # берём любое значение
            )
            .where(
                Filial.report_date >= start_date,
                Filial.report_date <= end_date
            )
            .group_by(Filial.name, Filial.owner)
        )
        return result.all()