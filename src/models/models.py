from sqlalchemy import (
    Boolean,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    company: Mapped["Company"] = relationship("Company", back_populates="employees")
    position_id: Mapped[int] = mapped_column(ForeignKey("position.id"), nullable=True)
    position: Mapped["Position"] = relationship("Position", back_populates="users")


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)
    employees: Mapped[list["User"]] = relationship("User", back_populates="company")


class Position(Base):
    __tablename__ = "position"
    __table_args__ = (
        UniqueConstraint(
            "name",
            "company_id",
            name="unique_position_in_company",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    users: Mapped[list["User"]] = relationship("User", back_populates="position")


class Invite(Base):
    __tablename__ = "invite"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    token: Mapped[str] = mapped_column(String, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
