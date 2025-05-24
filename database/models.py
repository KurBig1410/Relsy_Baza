from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import (
    String,
    Integer,
    BigInteger,
    Text,
    Column,
)  # noqa: F401


class Base(DeclarativeBase):
    pass


class AdminList(Base):
    __tablename__ = "admins"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=True)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, nullable=True)
    name: Mapped[str] = mapped_column(String(150), nullable=True)


class File(Base):
    __tablename__ = "files"
    id: Mapped[int] = mapped_column(
        Integer, autoincrement=True, primary_key=True, nullable=True
    )
    name: Mapped[str] = mapped_column(String(150), nullable=True)
    download_path: Mapped[str] = mapped_column(Text, nullable=True)
    img: Mapped[str] = mapped_column(Text, nullable=True)


class Folder(Base):
    __tablename__ = "folders"
    id: Mapped[int] = mapped_column(
        Integer, autoincrement=True, primary_key=True, nullable=True)
    name: Mapped[str] = mapped_column(String(150), nullable=True)
    path: Mapped[str] = mapped_column(Text, nullable=True)
    img: Mapped[str] = mapped_column(Text, nullable=True)


class FAQ(Base):
    __tablename__ = "faq"
    id = Column(String(3), primary_key=True)  # формат '001', '002', ...
    question = Column(String, nullable=False)
    answer = Column(String, nullable=False)
    department = Column(String, nullable=False) # отдел
    category = Column(String, nullable=False) # категория
