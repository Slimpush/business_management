from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils.types.ltree import LtreeType

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
    department_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("departments.id"), nullable=True
    )
    department: Mapped["Department"] = relationship(
        "Department", back_populates="employees", foreign_keys=[department_id]
    )
    managed_departments: Mapped[list["Department"]] = relationship(
        "Department", back_populates="manager", foreign_keys="Department.manager_id"
    )
    manager_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    manager: Mapped[Optional["User"]] = relationship(
        "User", remote_side="User.id", back_populates="subordinates"
    )
    subordinates: Mapped[list["User"]] = relationship("User", back_populates="manager")
    role_assignments: Mapped[list["RoleAssignment"]] = relationship(
        "RoleAssignment", back_populates="user"
    )


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)
    employees: Mapped[list["User"]] = relationship("User", back_populates="company")
    departments: Mapped[list["Department"]] = relationship(
        "Department", back_populates="company"
    )


class Position(Base):
    __tablename__ = "position"
    __table_args__ = (
        UniqueConstraint("name", "company_id", name="unique_position_in_company"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    users: Mapped[list["User"]] = relationship("User", back_populates="position")
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)


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
    path: Mapped[str] = mapped_column(LtreeType, index=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    manager_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    company: Mapped["Company"] = relationship("Company", back_populates="departments")
    manager: Mapped[Optional["User"]] = relationship(
        "User", back_populates="managed_departments", foreign_keys=[manager_id]
    )
    employees: Mapped[list["User"]] = relationship(
        "User", back_populates="department", foreign_keys="User.department_id"
    )
    role_assignments: Mapped[list["RoleAssignment"]] = relationship(
        "RoleAssignment", back_populates="department"
    )


class RoleAssignment(Base):
    __tablename__ = "role_assignments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    department_id: Mapped[int] = mapped_column(
        ForeignKey("departments.id"), nullable=False
    )
    role_name: Mapped[str] = mapped_column(String, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="role_assignments")
    department: Mapped["Department"] = relationship(
        "Department", back_populates="role_assignments"
    )
