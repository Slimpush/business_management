from typing import Optional
from sqlalchemy import (
    Boolean,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils import Ltree

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
    department_id: Mapped[Optional[int]] = mapped_column(ForeignKey("departments.id"), nullable=True)
    department: Mapped["Department"] = relationship("Department", back_populates="employees")
    managed_departments: Mapped[list["Department"]] = relationship("Department", back_populates="manager")


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)
    employees: Mapped[list["User"]] = relationship("User", back_populates="company")
    departments: Mapped[list["Department"]] = relationship("Department", back_populates="company")


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


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    path: Mapped[str] = mapped_column(Ltree, index=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    manager_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)

    company: Mapped["Company"] = relationship("Company", back_populates="departments")
    manager: Mapped[Optional["User"]] = relationship("User", back_populates="managed_departments")
    employees: Mapped[list["User"]] = relationship("User", back_populates="department")
