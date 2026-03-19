def test_get_all_market_values(client, sample_market_values):
    response = client.get("/market-values")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 4


def test_get_market_value_by_id(client, sample_market_values):
    market_value_id = sample_market_values[0].id

    response = client.get(f"/market-values/{market_value_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["player_name"] == "Mohamed Salah"
    assert data["current_value_gbp"] == 55000000


def test_get_market_value_not_found(client):
    response = client.get("/market-values/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Market value record not found"


def test_put_update_market_value(client, sample_market_values):
    market_value_id = sample_market_values[1].id

    payload = {
        "player_name": "Cole Palmer",
        "club_name": "Chelsea",
        "age": 22,
        "position": "AM",
        "position_group": "MID",
        "league_name": "Premier League",
        "current_value_gbp": 45000000,
        "peak_value_gbp": 50000000,
        "trajectory": "rising"
    }

    response = client.put(f"/market-values/{market_value_id}", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["player_name"] == "Cole Palmer"
    assert data["current_value_gbp"] == 45000000


def test_patch_market_value(client, sample_market_values):
    market_value_id = sample_market_values[2].id

    response = client.patch(
        f"/market-values/{market_value_id}",
        json={"current_value_gbp": 30000000}
    )
    assert response.status_code == 200

    data = response.json()
    assert data["player_name"] == "Virgil van Dijk"
    assert data["current_value_gbp"] == 30000000


def test_delete_market_value(client, sample_market_values):
    market_value_id = sample_market_values[3].id

    response = client.delete(f"/market-values/{market_value_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Market value record deleted successfully"

    get_response = client.get(f"/market-values/{market_value_id}")
    assert get_response.status_code == 404


def test_create_market_value(client):
    payload = {
        "player_name": "Bukayo Saka",
        "club_name": "Arsenal",
        "age": 23,
        "position": "RW",
        "position_group": "MID",
        "league_name": "Premier League",
        "current_value_gbp": 70000000,
        "peak_value_gbp": 75000000,
        "trajectory": "rising"
    }

    response = client.post("/market-values", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["player_name"] == "Bukayo Saka"
    assert data["club_name"] == "Arsenal"
    assert data["current_value_gbp"] == 70000000
    assert "id" in data