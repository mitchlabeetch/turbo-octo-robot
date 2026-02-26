"""
Workflow Automation models.

Provides a state machine engine for configurable business workflows.
"""

from sqlalchemy import (
    Boolean, Column, ForeignKey, Integer, String, Text,
)
from sqlalchemy.orm import relationship

from app.models.base import Base, SoftDeleteMixin, TenantMixin, TimestampMixin, UUIDMixin


class WorkflowTemplate(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, UUIDMixin):
    """Reusable workflow definition (state machine template)."""
    __tablename__ = "workflow_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    entity_type = Column(String(50), nullable=False, index=True)  # deal, invoice, expense_report, project
    is_active = Column(Boolean, default=True)

    states = relationship("WorkflowState", back_populates="template", lazy="selectin", cascade="all, delete-orphan")
    transitions = relationship("WorkflowTransition", back_populates="template", lazy="selectin", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<WorkflowTemplate({self.name} for {self.entity_type})>"


class WorkflowState(Base, TimestampMixin, TenantMixin):
    """State within a workflow template."""
    __tablename__ = "workflow_states"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("workflow_templates.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    state_type = Column(String(20), default="intermediate")  # initial, intermediate, terminal
    color = Column(String(7), default="#6B7280")

    template = relationship("WorkflowTemplate", back_populates="states")

    def __repr__(self) -> str:
        return f"<WorkflowState({self.name})>"


class WorkflowTransition(Base, TimestampMixin, TenantMixin):
    """Allowed transition between states."""
    __tablename__ = "workflow_transitions"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("workflow_templates.id"), nullable=False, index=True)
    from_state_id = Column(Integer, ForeignKey("workflow_states.id"), nullable=False, index=True)
    to_state_id = Column(Integer, ForeignKey("workflow_states.id"), nullable=False, index=True)
    trigger_name = Column(String(100), nullable=False)  # e.g. "approve", "reject", "submit"
    required_role = Column(String(50), nullable=True)  # Role required to trigger
    conditions_json = Column(Text, nullable=True)  # JSON conditions

    template = relationship("WorkflowTemplate", back_populates="transitions")
    from_state = relationship("WorkflowState", foreign_keys=[from_state_id])
    to_state = relationship("WorkflowState", foreign_keys=[to_state_id])

    def __repr__(self) -> str:
        return f"<WorkflowTransition({self.trigger_name}: {self.from_state_id} → {self.to_state_id})>"


class WorkflowInstance(Base, TimestampMixin, TenantMixin, UUIDMixin):
    """Active workflow instance attached to an entity."""
    __tablename__ = "workflow_instances"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("workflow_templates.id"), nullable=False, index=True)
    current_state_id = Column(Integer, ForeignKey("workflow_states.id"), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(Integer, nullable=False, index=True)

    template = relationship("WorkflowTemplate")
    current_state = relationship("WorkflowState")

    def __repr__(self) -> str:
        return f"<WorkflowInstance({self.entity_type}:{self.entity_id}, state={self.current_state_id})>"
