"""
Project & Resource Management models.

Covers: projects, tasks, time tracking, capacity planning.
"""

from sqlalchemy import (
    Boolean, Column, Date, DateTime, Float, ForeignKey,
    Integer, Numeric, String, Text,
)
from sqlalchemy.orm import relationship

from app.models.base import Base, SoftDeleteMixin, TenantMixin, TimestampMixin, UUIDMixin


class Project(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, UUIDMixin):
    """Project linked to a deal or standalone."""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="active", index=True)  # planning, active, on_hold, completed, cancelled
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    budget = Column(Numeric(precision=14, scale=2), nullable=True)
    currency = Column(String(3), default="EUR")

    tasks = relationship("Task", back_populates="project", lazy="selectin", cascade="all, delete-orphan")
    owner = relationship("User")

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name='{self.name}')>"


class Task(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, UUIDMixin):
    """Individual task within a project."""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="todo", index=True)  # todo, in_progress, review, done, blocked
    priority = Column(String(20), default="medium", index=True)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    due_date = Column(Date, nullable=True)
    estimated_hours = Column(Float, nullable=True)
    actual_hours = Column(Float, default=0)

    project = relationship("Project", back_populates="tasks")
    assignee = relationship("User")
    time_entries = relationship("TimeEntry", back_populates="task", lazy="noload", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, title='{self.title}', status='{self.status}')>"


class TimeEntry(Base, TimestampMixin, TenantMixin):
    """Time tracking entry."""
    __tablename__ = "time_entries"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    hours = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    billable = Column(Boolean, default=True)
    hourly_rate = Column(Numeric(precision=10, scale=2), nullable=True)
    invoiced = Column(Boolean, default=False)

    task = relationship("Task", back_populates="time_entries")
    user = relationship("User")

    def __repr__(self) -> str:
        return f"<TimeEntry(user={self.user_id}, hours={self.hours}, date={self.date})>"
