"""Tests for Phase 4-10 models: projects, workflows, reporting, integrations."""

from datetime import date, datetime, timezone
from decimal import Decimal

from app.models.projects import Project, Task, TimeEntry
from app.models.workflows import WorkflowTemplate, WorkflowState, WorkflowTransition, WorkflowInstance
from app.models.reporting import ReportDefinition, Dashboard, DashboardWidget, Notification
from app.models.integrations import (
    AuditLog, Permission, RolePermission, ApiKey, Tag, EntityTag,
    Address, CustomFieldDefinition, CustomFieldValue,
    IntegrationConfig, SyncLog,
)


class TestProjectModels:

    def test_project_creation(self, db_session):
        project = Project(
            name="Test Project", status="active",
            tenant_id="default", budget=Decimal("50000"),
        )
        db_session.add(project)
        db_session.commit()
        assert project.id is not None
        assert project.uuid is not None
        assert str(project) == f"<Project(id={project.id}, name='Test Project')>"

    def test_task_creation(self, db_session):
        project = Project(name="P", tenant_id="default")
        db_session.add(project)
        db_session.flush()
        task = Task(
            project_id=project.id, title="Review", status="in_progress",
            priority="high", estimated_hours=8.0, tenant_id="default",
        )
        db_session.add(task)
        db_session.commit()
        assert task.uuid is not None
        assert str(task) == f"<Task(id={task.id}, title='Review', status='in_progress')>"

    def test_time_entry(self, db_session, test_user):
        entry = TimeEntry(
            user_id=test_user.id, date=date(2026, 1, 15),
            hours=4.5, billable=True, tenant_id="default",
        )
        db_session.add(entry)
        db_session.commit()
        assert entry.id is not None
        assert str(entry) == f"<TimeEntry(user={test_user.id}, hours=4.5, date=2026-01-15)>"


class TestWorkflowModels:

    def test_workflow_template(self, db_session):
        template = WorkflowTemplate(
            name="Invoice Approval", entity_type="invoice",
            tenant_id="default",
        )
        db_session.add(template)
        db_session.commit()
        assert template.uuid is not None
        assert str(template) == "<WorkflowTemplate(Invoice Approval for invoice)>"

    def test_workflow_state(self, db_session):
        template = WorkflowTemplate(
            name="WF", entity_type="deal", tenant_id="default",
        )
        db_session.add(template)
        db_session.flush()
        state = WorkflowState(
            template_id=template.id, name="Pending Review",
            state_type="intermediate", tenant_id="default",
        )
        db_session.add(state)
        db_session.commit()
        assert str(state) == "<WorkflowState(Pending Review)>"

    def test_workflow_transition(self, db_session):
        template = WorkflowTemplate(
            name="WF", entity_type="deal", tenant_id="default",
        )
        db_session.add(template)
        db_session.flush()
        s1 = WorkflowState(template_id=template.id, name="Draft", tenant_id="default")
        s2 = WorkflowState(template_id=template.id, name="Submitted", tenant_id="default")
        db_session.add_all([s1, s2])
        db_session.flush()
        trans = WorkflowTransition(
            template_id=template.id, from_state_id=s1.id, to_state_id=s2.id,
            trigger_name="submit", tenant_id="default",
        )
        db_session.add(trans)
        db_session.commit()
        assert str(trans) == f"<WorkflowTransition(submit: {s1.id} → {s2.id})>"

    def test_workflow_instance(self, db_session):
        template = WorkflowTemplate(name="WF", entity_type="invoice", tenant_id="default")
        db_session.add(template)
        db_session.flush()
        state = WorkflowState(template_id=template.id, name="Open", tenant_id="default")
        db_session.add(state)
        db_session.flush()
        inst = WorkflowInstance(
            template_id=template.id, current_state_id=state.id,
            entity_type="invoice", entity_id=42, tenant_id="default",
        )
        db_session.add(inst)
        db_session.commit()
        assert inst.uuid is not None


class TestReportingModels:

    def test_report_definition(self, db_session):
        report = ReportDefinition(
            name="Pipeline Report", report_type="pipeline",
            config_json='{"stages": "all"}', tenant_id="default",
        )
        db_session.add(report)
        db_session.commit()
        assert report.uuid is not None

    def test_dashboard_with_widgets(self, db_session, test_user):
        dash = Dashboard(
            name="Main Dashboard", owner_id=test_user.id,
            is_default=True, tenant_id="default",
        )
        db_session.add(dash)
        db_session.flush()
        widget = DashboardWidget(
            dashboard_id=dash.id, widget_type="kpi_card",
            title="Revenue", config_json='{"metric": "revenue"}',
            tenant_id="default",
        )
        db_session.add(widget)
        db_session.commit()
        assert len(dash.widgets) == 1

    def test_notification(self, db_session, test_user):
        notif = Notification(
            user_id=test_user.id, title="Deal Updated",
            notification_type="deal_update", tenant_id="default",
        )
        db_session.add(notif)
        db_session.commit()
        assert notif.is_read is False


class TestIntegrationModels:

    def test_audit_log(self, db_session):
        log = AuditLog(
            action="create", entity_type="deal", entity_id=1,
            changes_json='{"title": "New Deal"}', tenant_id="default",
        )
        db_session.add(log)
        db_session.commit()
        assert str(log) == "<AuditLog(create deal:1)>"

    def test_permission_and_role(self, db_session):
        perm = Permission(
            codename="deals.create", name="Create Deals",
            module="deals", tenant_id="default",
        )
        db_session.add(perm)
        db_session.flush()
        rp = RolePermission(
            role="advisor", permission_id=perm.id, tenant_id="default",
        )
        db_session.add(rp)
        db_session.commit()
        assert str(perm) == "<Permission(deals.create)>"

    def test_api_key(self, db_session, test_user):
        key = ApiKey(
            name="CI/CD Key", key_hash="sha256:abcdef",
            user_id=test_user.id, tenant_id="default",
        )
        db_session.add(key)
        db_session.commit()
        assert key.uuid is not None

    def test_tag_and_entity_tag(self, db_session):
        tag = Tag(name="Technology", color="#3B82F6", category="sector", tenant_id="default")
        db_session.add(tag)
        db_session.flush()
        et = EntityTag(
            tag_id=tag.id, entity_type="company", entity_id=1,
            tenant_id="default",
        )
        db_session.add(et)
        db_session.commit()
        assert str(tag) == "<Tag(Technology)>"

    def test_address(self, db_session):
        addr = Address(
            entity_type="company", entity_id=1,
            line1="123 Main St", city="Paris", country="FR",
            is_primary=True, tenant_id="default",
        )
        db_session.add(addr)
        db_session.commit()
        assert addr.uuid is not None
        assert str(addr) == "<Address(Paris, FR)>"

    def test_custom_field(self, db_session):
        defn = CustomFieldDefinition(
            entity_type="deal", field_name="industry_code",
            field_type="text", tenant_id="default",
        )
        db_session.add(defn)
        db_session.flush()
        val = CustomFieldValue(
            definition_id=defn.id, entity_type="deal", entity_id=1,
            value_text="TECH-001", tenant_id="default",
        )
        db_session.add(val)
        db_session.commit()
        assert str(defn) == "<CustomFieldDefinition(industry_code on deal)>"

    def test_integration_config(self, db_session):
        config = IntegrationConfig(
            provider="pipedrive", is_active=True, tenant_id="default",
        )
        db_session.add(config)
        db_session.flush()
        log = SyncLog(
            integration_id=config.id, sync_type="full",
            status="success", records_synced=150, tenant_id="default",
        )
        db_session.add(log)
        db_session.commit()
        assert str(config) == "<IntegrationConfig(pipedrive, active=True)>"
        assert str(log) == f"<SyncLog(integration={config.id}, status='success')>"
