import pytest

from app.main import app, validate_report, _reports


@pytest.fixture
def client():
    _reports.clear()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"


def test_valid_report_passes_validation():
    assert validate_report({"location": "شارع المطار", "type": "collision"}) == []


def test_short_location_is_rejected():
    assert validate_report({"location": "a", "type": "other"})


def test_unknown_type_is_rejected():
    assert validate_report({"location": "شارع المطار", "type": "fire"})


def test_create_and_list_report(client):
    r = client.post("/api/reports", json={"location": "شارع المطار", "type": "breakdown"})
    assert r.status_code == 201
    assert client.get("/api/reports").get_json()[0]["id"] == 1


def test_invalid_report_returns_400(client):
    r = client.post("/api/reports", json={"location": ""})
    assert r.status_code == 400

def test_long_plate_is_rejected():
    data = {"location": "Airport Road", "type": "other", "plate": "12345678901"}
    errors = validate_report(data)
    assert "plate must be 10 characters or less" in errors

