import pytest
import ACEest_Fitness


@pytest.fixture
def client(tmp_path):
    ACEest_Fitness.DB_NAME = str(tmp_path / "test_aceest.db")
    ACEest_Fitness.init_db()
    ACEest_Fitness.app.config["TESTING"] = True
    with ACEest_Fitness.app.test_client() as test_client:
        yield test_client


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json()["status"] == "healthy"


def test_programs(client):
    res = client.get("/programs")
    assert res.status_code == 200
    assert "Muscle Gain (MG)" in res.get_json()


def test_create_and_fetch_client(client):
    payload = {
        "name": "Rashi",
        "age": 28,
        "height": 165,
        "weight": 60,
        "program": "Fat Loss (FL)",
    }
    post_res = client.post("/clients", json=payload)
    assert post_res.status_code == 201
    assert post_res.get_json()["calories"] == 1320

    get_res = client.get("/clients/Rashi")
    assert get_res.status_code == 200
    assert get_res.get_json()["name"] == "Rashi"


def test_invalid_client_payload(client):
    res = client.post("/clients", json={"name": "", "program": "Unknown"})
    assert res.status_code == 400


def test_bmi_endpoint(client):
    res = client.post("/bmi", json={"height": 170, "weight": 68})
    assert res.status_code == 200
    assert res.get_json() == {"bmi": 23.5, "category": "Normal"}
