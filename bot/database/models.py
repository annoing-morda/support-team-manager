"""SQLAlchemy models for the application."""

from datetime import date, datetime

from sqlalchemy import (
    BIGINT,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


class Employee(Base):
    """Employee (team member) model."""

    __tablename__ = "employees"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Telegram information
    telegram_id: Mapped[int] = mapped_column(
        BIGINT, unique=True, nullable=False, index=True
    )
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Permissions and status
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationships
    duties: Mapped[list["Duty"]] = relationship(
        "Duty", back_populates="employee", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<Employee(id={self.id}, telegram_id={self.telegram_id}, "
            f"username='{self.username}', full_name='{self.full_name}')>"
        )


class Duty(Base):
    """Duty assignment model."""

    __tablename__ = "duties"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign key
    employee_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Duty information
    date: Mapped[date] = mapped_column(Date, unique=True, nullable=False, index=True)
    notified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationships
    employee: Mapped["Employee"] = relationship("Employee", back_populates="duties")

    def __repr__(self) -> str:
        return (
            f"<Duty(id={self.id}, employee_id={self.employee_id}, "
            f"date={self.date}, notified={self.notified})>"
        )
