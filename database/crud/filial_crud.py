# crud/filial_crud.py
from sqlmodel import select, delete
from data_base.filial import Filial

from data_base.engine import session_maker

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


async def get_filial_by_name(session, name: str):
    result = await session.exec(select(Filial).where(Filial.name == name))
    return result.first()


async def clear_filial_table():
    async with async_session() as session:
        async with session.begin():
            await session.exec(delete(Filial))
        print("✅ Таблица filial очищена.")
