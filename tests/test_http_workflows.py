import json
from pathlib import Path

from fastapi.testclient import TestClient

from main import app

ROOT = Path(__file__).resolve().parents[1]


def test_stack_exposes_adk_and_sub_agents():
    with TestClient(app) as client:
        res = client.get("/api/stack")
        assert res.status_code == 200
        body = res.json()
        assert body["adk"] is True
        assert body["root_agent"] == "matrix_orchestrator"
        assert "hazard_scanner" in body["sub_agents"]
        assert body["apps"] == ["matrix"]
        assert "parallel_configured" in body


def test_list_apps_discovers_matrix():
    with TestClient(app) as client:
        res = client.get("/list-apps")
        assert res.status_code == 200
        assert "matrix" in res.json()


def test_sample_to_analyze_workflow():
    with TestClient(app) as client:
        sample = client.get("/api/sample").json()
        assert "SCENE 12" in sample["script_text"]
        res = client.post(
            "/api/analyze",
            json={
                "production_title": sample["callsheet"]["production"],
                "script_text": sample["script_text"],
                "callsheet": sample["callsheet"],
                "location_name": sample["callsheet"]["location"],
                "shoot_date": sample["callsheet"]["shoot_date"],
                "project_context": sample["project_context"],
            },
        )
        assert res.status_code == 200
        brief = res.json()
        assert brief["parsed_scene_count"] == 4
        assert brief["executive_summary"]["overall_label"] in {"CRITICAL", "HIGH", "MODERATE", "MANAGEABLE"}
        assert any(r["category"] == "Production Activities" for r in brief["risk_register"])
        pyro = [r for r in brief["risk_register"] if "Pyro" in r.get("subsection", "") or "pyro" in r["hazard"].lower()]
        assert pyro
        assert pyro[0]["controls"]
        assert brief["thesis"]["collisions"]
        assert brief["agent_trace"][0]["tool"] == "scan_scene_for_hazards"


def test_agent_ask_requires_key_when_missing(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_GENAI_USE_VERTEXAI", raising=False)
    with TestClient(app) as client:
        res = client.post("/api/agent/ask", json={"message": "hello"})
        assert res.status_code == 503
