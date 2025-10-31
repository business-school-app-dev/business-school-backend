from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    String,
    BigInteger,
    DateTime,
    text,
    JSON,
    ForeignKey
)

from app import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    password_hash: Mapped[Optional[str]] = mapped_column(String(255))
    username: Mapped[Optional[str]] = mapped_column(String(64), unique=True)
    name: Mapped[Optional[str]] = mapped_column(String(255))

    role: Mapped[str] = mapped_column(String(16))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
    )
    
    trophies: Mapped[int] = mapped_column(BigInteger)
    retirement_age: Mapped[Optional[int]] = mapped_column()
    employment_age: Mapped[Optional[int]] = mapped_column()

    career_name: Mapped[Optional[str]] = mapped_column(String(64))
    career_starting: Mapped[Optional[int]] = mapped_column()
    career_growth: Mapped[Optional[float]] = mapped_column()

    children: Mapped[Optional[int]] = mapped_column()

    monthly_spending: Mapped[Optional[int]] = mapped_column()

class FinStatements(Base):
    __tablename__ = "statements"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id'))

    name: Mapped[str] = mapped_column(String[255])
    valuation: Mapped[int] = mapped_column(BigInteger)
    growth: Mapped[float] = mapped_column()
    term: Mapped[Optional[int]] = mapped_column()

    liab_status: Mapped[bool] = mapped_column()


class Questions(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    question_difficulty: Mapped[int] = mapped_column()
    question: Mapped[str] = mapped_column(String[255])
    question_choices: Mapped[JSON] = mapped_column(JSON)

    correct_answer: Mapped[int] = mapped_column()

class Jobs(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    name: Mapped[str] = mapped_column(String[64])
    starting: Mapped[int] = mapped_column()
    growth: Mapped[float] = mapped_column()
