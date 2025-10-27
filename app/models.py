from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    String,
    BigInteger,
    DateTime,
    text,
)

from app import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    password_hash: Mapped[Optional[str]] = mapped_column(String(255))
    username: Mapped[Optional[str]] = mapped_column(String(64), unique=True)
    name: Mapped[Optional[str]] = mapped_column(String(255))

    role: Mapped[str] = mapped_column(String(16), server_default="student")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
    )


