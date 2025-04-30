from sqlmodel import SQLModel, Field
from typing import Optional


class Base(SQLModel):
    pass


class Filial(Base, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    income: Optional[float] = None
    service_sum: Optional[float] = None
    goods_sum: Optional[float] = None
    avg_check_total: Optional[float] = None
    avg_check_service: Optional[float] = None
    avg_filling: Optional[float] = None
    new_clients: Optional[int] = None
    repeat_clients: Optional[int] = None
    lost_clients: Optional[int] = None
    total_appointments: Optional[int] = None
    canceled_appointments: Optional[int] = None
    finished_appointments: Optional[int] = None
    unfinished_appointments: Optional[int] = None
    population_category: Optional[str] = None
    owner: Optional[str] = None
