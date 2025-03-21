from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Date, String, JSON, Integer, Time, BigInteger, Text  # noqa: F401


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
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True, nullable=True)
    name: Mapped[str] = mapped_column(String(150), nullable=True)
    download_path: Mapped[str] = mapped_column(Text, nullable=True)
    img: Mapped[str] = mapped_column(Text, nullable=True)


class Folder(Base):
    __tablename__ = "folders"
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True, nullable=True)
    name: Mapped[str] = mapped_column(String(150), nullable=True)
    path: Mapped[str] = mapped_column(Text, nullable=True)
    img: Mapped[str] = mapped_column(Text, nullable=True)
