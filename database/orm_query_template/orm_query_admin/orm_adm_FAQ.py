from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from database.models import FAQ


# Добавление вопросов в FAQ
async def orm_add_question(session: AsyncSession, data: dict):
    obj = FAQ(
        id=data["id"],
        question=data["question"],
        answer=data["answer"],
        category=data["category"],
        department=data["department"],
    )
    session.add(obj)
    await session.commit()


# Получение списка вопросов
async def orm_get_question(session: AsyncSession):
    query = select(FAQ)
    result = await session.execute(query)
    return result.scalars().all()


# Получение вопроса по id
async def orm_get_question_by_id(question_id, session: AsyncSession):
    query = select(FAQ).where(FAQ.id == question_id)
    result = await session.execute(query)
    return result.scalars().all()


# Получение вопроса по отделу
async def orm_get_question_by_department(department, session: AsyncSession):
    query = select(FAQ).where(FAQ.department == department)
    result = await session.execute(query)
    return result.scalars().all()


# Получение вопроса по категории
async def orm_get_question_by_category(category, session: AsyncSession):
    query = select(FAQ).where(FAQ.category == category)
    result = await session.execute(query)
    return result.scalars().all()


# Получение категории по отделу
async def orm_get_category_by_department(department, session: AsyncSession):
    query = select(FAQ).where(FAQ.department == department)
    result = await session.execute(query)
    return result.scalars().all()


# Удаление таблицы с вопросами
async def orm_delete_faqs(session: AsyncSession):
    query = delete(FAQ)
    result = await session.execute(query)
    await session.commit()
    return result.rowcount


# Удаление вопроса по id
async def orm_delete_faqs_by_id(session: AsyncSession, faq_id):
    query = delete(FAQ).where(FAQ.id == faq_id)
    result = await session.execute(query)
    await session.commit()
    return result.rowcount
