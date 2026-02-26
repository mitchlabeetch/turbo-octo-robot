"""Tests for Deal management endpoints and service."""

from decimal import Decimal

from app.models.deals import DealStage
from app.services.deals import DealService, seed_default_stages


class TestDealStageSeeding:
    """Verify default M&A stage seeding."""

    def test_seed_creates_12_stages(self, db_session):
        stages = seed_default_stages(db_session, tenant_id="default")
        assert len(stages) == 12
        assert stages[0].name == "Origination"
        assert stages[-1].name == "Post-Closing"
        assert stages[-1].is_won is True

    def test_seed_is_idempotent(self, db_session):
        seed_default_stages(db_session, tenant_id="default")
        stages = seed_default_stages(db_session, tenant_id="default")
        assert len(stages) == 12


class TestDealService:
    """Verify DealService business logic."""

    def _seed_and_svc(self, db_session):
        stages = seed_default_stages(db_session, tenant_id="default")
        svc = DealService(db_session, tenant_id="default")
        return svc, stages

    def test_create_deal(self, db_session):
        svc, stages = self._seed_and_svc(db_session)
        deal = svc.create({
            "title": "Acme Acquisition",
            "deal_type": "sell-side",
            "stage_id": stages[0].id,
            "target_value": Decimal("10000000"),
        })
        assert deal.id is not None
        assert deal.title == "Acme Acquisition"
        assert deal.uuid is not None

    def test_update_deal_logs_stage_change(self, db_session):
        svc, stages = self._seed_and_svc(db_session)
        deal = svc.create({"title": "Test Deal", "deal_type": "sell-side", "stage_id": stages[0].id})
        svc.update(deal.id, {"stage_id": stages[1].id}, user_id=1)
        activities = svc.get_activities(deal.id)
        stage_changes = [a for a in activities if a.activity_type == "stage_change"]
        assert len(stage_changes) == 1

    def test_deal_notes(self, db_session):
        svc, stages = self._seed_and_svc(db_session)
        deal = svc.create({"title": "Note Deal", "deal_type": "buy-side", "stage_id": stages[0].id})
        note = svc.add_note(deal.id, author_id=1, content="Important update")
        assert note.content == "Important update"
        notes = svc.get_notes(deal.id)
        assert len(notes) == 1

    def test_deal_team(self, db_session, test_user):
        svc, stages = self._seed_and_svc(db_session)
        deal = svc.create({"title": "Team Deal", "deal_type": "sell-side", "stage_id": stages[0].id})
        member = svc.add_team_member(deal.id, test_user.id, role="lead_advisor")
        assert member.role == "lead_advisor"
        team = svc.get_team(deal.id)
        assert len(team) == 1

    def test_buyer_list(self, db_session):
        svc, stages = self._seed_and_svc(db_session)
        deal = svc.create({"title": "BL Deal", "deal_type": "sell-side", "stage_id": stages[0].id})
        bl = svc.create_buyer_list(deal.id, {"name": "Strategic Buyers", "list_type": "buyers"})
        assert bl.name == "Strategic Buyers"
        entry = svc.add_buyer_list_entry(bl.id, {"status": "identified", "priority": "high"})
        assert entry.status == "identified"
        lists = svc.get_buyer_lists(deal.id)
        assert len(lists) == 1

    def test_deal_bids(self, db_session):
        svc, stages = self._seed_and_svc(db_session)
        deal = svc.create({"title": "Bid Deal", "deal_type": "sell-side", "stage_id": stages[0].id})
        bid = svc.add_bid(deal.id, {"bid_type": "indicative", "amount": Decimal("5000000")})
        assert bid.bid_type == "indicative"
        assert bid.submitted_at is not None
        bids = svc.get_bids(deal.id)
        assert len(bids) == 1

    def test_soft_delete_deal(self, db_session):
        svc, stages = self._seed_and_svc(db_session)
        deal = svc.create({"title": "Delete Me", "deal_type": "sell-side", "stage_id": stages[0].id})
        assert svc.count() == 1
        svc.delete(deal.id)
        assert svc.count() == 0

    def test_pipeline_view(self, db_session):
        svc, stages = self._seed_and_svc(db_session)
        svc.create({"title": "Deal A", "deal_type": "sell-side", "stage_id": stages[0].id, "target_value": Decimal("1000000")})
        svc.create({"title": "Deal B", "deal_type": "sell-side", "stage_id": stages[0].id, "target_value": Decimal("2000000")})
        svc.create({"title": "Deal C", "deal_type": "buy-side", "stage_id": stages[2].id, "target_value": Decimal("5000000")})
        pipeline = svc.get_pipeline_view()
        assert len(pipeline) == 12  # All stages shown
        origination = pipeline[0]
        assert origination["deal_count"] == 2
        assert origination["total_value"] == Decimal("3000000")


class TestDealEndpoints:
    """Verify deal REST API endpoints."""

    def test_list_stages(self, auth_client):
        response = auth_client.get("/deals/stages")
        assert response.status_code == 200
        stages = response.json()
        assert len(stages) == 12

    def test_create_and_get_deal(self, auth_client):
        # Get stages first
        stages = auth_client.get("/deals/stages").json()
        # Create deal
        response = auth_client.post("/deals", json={
            "title": "Test Acquisition",
            "deal_type": "sell-side",
            "stage_id": stages[0]["id"],
            "target_value": "10000000",
            "currency": "EUR",
        })
        assert response.status_code == 200
        deal = response.json()
        assert deal["title"] == "Test Acquisition"
        assert deal["uuid"] is not None
        # Get deal
        get_resp = auth_client.get(f"/deals/{deal['id']}")
        assert get_resp.status_code == 200
        assert get_resp.json()["title"] == "Test Acquisition"

    def test_deal_not_found(self, auth_client):
        response = auth_client.get("/deals/99999")
        assert response.status_code == 404

    def test_update_deal(self, auth_client):
        stages = auth_client.get("/deals/stages").json()
        create_resp = auth_client.post("/deals", json={
            "title": "Update Me", "deal_type": "buy-side", "stage_id": stages[0]["id"],
        })
        deal_id = create_resp.json()["id"]
        update_resp = auth_client.patch(f"/deals/{deal_id}", json={"title": "Updated Title"})
        assert update_resp.status_code == 200
        assert update_resp.json()["title"] == "Updated Title"

    def test_delete_deal(self, auth_client):
        stages = auth_client.get("/deals/stages").json()
        create_resp = auth_client.post("/deals", json={
            "title": "Delete Me", "deal_type": "sell-side", "stage_id": stages[0]["id"],
        })
        deal_id = create_resp.json()["id"]
        del_resp = auth_client.delete(f"/deals/{deal_id}")
        assert del_resp.status_code == 200
        get_resp = auth_client.get(f"/deals/{deal_id}")
        assert get_resp.status_code == 404  # Soft-deleted

    def test_deal_notes_api(self, auth_client):
        stages = auth_client.get("/deals/stages").json()
        deal = auth_client.post("/deals", json={
            "title": "Note Deal", "deal_type": "sell-side", "stage_id": stages[0]["id"],
        }).json()
        # Add note
        note_resp = auth_client.post(f"/deals/{deal['id']}/notes", json={"content": "Test note"})
        assert note_resp.status_code == 200
        # List notes
        notes = auth_client.get(f"/deals/{deal['id']}/notes").json()
        assert len(notes) == 1

    def test_pipeline_view_api(self, auth_client):
        stages = auth_client.get("/deals/stages").json()
        auth_client.post("/deals", json={
            "title": "Pipeline Deal", "deal_type": "sell-side", "stage_id": stages[0]["id"],
        })
        response = auth_client.get("/deals/pipeline")
        assert response.status_code == 200
        pipeline = response.json()
        assert len(pipeline) == 12
