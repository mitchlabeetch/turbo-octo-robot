"""
Reporting & Dashboard models.

Provides saved report definitions and dashboard configurations.
"""

from sqlalchemy import (
    Boolean, Column, ForeignKey, Integer, String, Text,
)
from sqlalchemy.orm import relationship

from app.models.base import Base, SoftDeleteMixin, TenantMixin, TimestampMixin, UUIDMixin


class ReportDefinition(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, UUIDMixin):
    """Saved report configuration."""
    __tablename__ = "report_definitions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    report_type = Column(String(50), nullable=False, index=True)  # pipeline, revenue, aging, activity, custom
    description = Column(Text, nullable=True)
    config_json = Column(Text, nullable=False)  # Full report configuration as JSON
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    is_shared = Column(Boolean, default=False)

    owner = relationship("User")

    def __repr__(self) -> str:
        return f"<ReportDefinition({self.name}, type='{self.report_type}')>"


class Dashboard(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, UUIDMixin):
    """User dashboard configuration."""
    __tablename__ = "dashboards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    is_default = Column(Boolean, default=False)
    layout_json = Column(Text, nullable=True)  # Grid layout configuration

    owner = relationship("User")
    widgets = relationship("DashboardWidget", back_populates="dashboard", lazy="selectin", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Dashboard({self.name})>"


class DashboardWidget(Base, TimestampMixin, TenantMixin):
    """Individual widget on a dashboard."""
    __tablename__ = "dashboard_widgets"

    id = Column(Integer, primary_key=True, index=True)
    dashboard_id = Column(Integer, ForeignKey("dashboards.id"), nullable=False, index=True)
    widget_type = Column(String(50), nullable=False)  # kpi_card, chart, table, pipeline, calendar
    title = Column(String(255), nullable=True)
    config_json = Column(Text, nullable=True)  # Widget-specific configuration
    position_x = Column(Integer, default=0)
    position_y = Column(Integer, default=0)
    width = Column(Integer, default=4)
    height = Column(Integer, default=3)

    dashboard = relationship("Dashboard", back_populates="widgets")

    def __repr__(self) -> str:
        return f"<DashboardWidget({self.widget_type}, title='{self.title}')>"


class Notification(Base, TimestampMixin, TenantMixin):
    """User notification."""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=True)
    notification_type = Column(String(50), nullable=False, index=True)  # deal_update, task_assigned, invoice_paid, etc.
    entity_type = Column(String(50), nullable=True)
    entity_id = Column(Integer, nullable=True)
    is_read = Column(Boolean, default=False, index=True)

    user = relationship("User")

    def __repr__(self) -> str:
        return f"<Notification(user={self.user_id}, type='{self.notification_type}')>"
