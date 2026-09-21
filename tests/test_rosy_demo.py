import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "landing_page"))
from rosy_demo import create_workspace, load_workspace, transition_workspace
from brief_receiver import readiness_payload


def brief(name="Rosy Rivera", needs=None, market="Estero & Naples, FL"):
    return {"answers": {"full_name": name, "market": market, "needs": needs or ["follow_up", "intake"]}}


def test_receiver_payload_creates_tenant_scoped_manifest(tmp_path):
    one = create_workspace(brief(), tmp_path)
    two = create_workspace(brief("Other Realtor", ["copy"]), tmp_path)
    assert one["tenant_id"] != two["tenant_id"]
    assert load_workspace(tmp_path, one["tenant_id"])["tenant_id"] == one["tenant_id"]
    assert all(c["synthetic"] for c in one["contacts"])
    assert one["source_needs"] == ["follow_up", "intake"]
    assert one["claims"]["agent_deployed"] is False


def test_tenant_isolation_rejects_cross_tenant_item(tmp_path):
    one = create_workspace(brief(), tmp_path)
    two = create_workspace(brief("Other"), tmp_path)
    try:
        transition_workspace(tmp_path, one["tenant_id"], two["queue"][0]["item_id"], "skip")
    except KeyError:
        pass
    else:
        raise AssertionError("cross-tenant item was accepted")


def test_queue_state_transitions_and_next_dates(tmp_path):
    workspace = create_workspace(brief(), tmp_path)
    item = next(i for i in workspace["queue"] if i["status"] == "waiting_approval")
    approved = transition_workspace(tmp_path, workspace["tenant_id"], item["item_id"], "approve")
    result = next(i for i in approved["queue"] if i["item_id"] == item["item_id"])
    assert result["status"] == "approved_for_manual_send"
    assert result["send_evidence"].startswith("manual-copy-ready")
    assert result["next_follow_up_at"]
    other = next(i for i in approved["queue"] if i["status"] == "waiting_approval")
    snoozed = transition_workspace(tmp_path, workspace["tenant_id"], other["item_id"], "snooze", "2099-01-02")
    assert next(i for i in snoozed["queue"] if i["item_id"] == other["item_id"])["status"] == "snoozed"


def test_secret_rejection(tmp_path):
    try:
        create_workspace({"answers": {"full_name": "Bad", "api_key": "not accepted"}}, tmp_path)
    except ValueError as err:
        assert "credentials" in str(err)
    else:
        raise AssertionError("secret was accepted")


def test_no_send_behavior(tmp_path):
    workspace = create_workspace(brief(), tmp_path)
    assert workspace["send_gate"] == "EXTERNAL_SEND_DISABLED_COPY_READY_ONLY"
    item = next(i for i in workspace["queue"] if i["status"] == "waiting_approval")
    after = transition_workspace(tmp_path, workspace["tenant_id"], item["item_id"], "approve")
    assert next(i for i in after["queue"] if i["item_id"] == item["item_id"])["send_evidence"] == "manual-copy-ready; external send disabled"
    assert not (tmp_path / "outbound").exists()


def test_readiness_payload_is_local_and_explicitly_gated():
    readiness = readiness_payload()
    assert readiness["ok"] is True
    assert readiness["bind"] == "127.0.0.1:8787"
    assert readiness["surfaces"]["workspace"]["status"] == "ready"
    assert readiness["surfaces"]["external_integrations"]["status"] == "disabled"
    assert readiness["claims"]["direct_publishing"] is False
