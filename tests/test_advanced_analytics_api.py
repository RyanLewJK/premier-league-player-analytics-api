def test_get_player_availability(client, sample_players):
    player_id = sample_players[0].id

    response = client.get(f"/advanced-analytics/player/{player_id}/availability")
    assert response.status_code == 200

    data = response.json()
    assert data["player_name"] == "Mohamed Salah"
    assert "availability_factor" in data


def test_get_player_availability_not_found(client):
    response = client.get("/advanced-analytics/player/9999/availability")
    assert response.status_code == 404
    assert response.json()["detail"] == "Player not found"


def test_compare_players(client, sample_players, sample_market_values):
    response = client.get(
        "/advanced-analytics/compare?player1=Mohamed Salah&player2=Cole Palmer"
    )
    assert response.status_code == 200

    data = response.json()
    assert "player_1" in data
    assert "player_2" in data
    assert data["player_1"]["player_name"] == "Mohamed Salah"
    assert data["player_2"]["player_name"] == "Cole Palmer"
    assert "better_performer" in data


def test_compare_players_not_found(client, sample_players, sample_market_values):
    response = client.get(
        "/advanced-analytics/compare?player1=Mohamed Salah&player2=Unknown Player"
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "One or both players not found"


def test_filter_players_by_position_and_minutes(client, sample_players, sample_market_values):
    response = client.get("/advanced-analytics/filter?position=MID&min_minutes=2000")
    assert response.status_code == 200

    data = response.json()
    assert len(data) > 0
    assert all(player["position"] == "MID" for player in data)


def test_filter_players_by_club(client, sample_players, sample_market_values):
    response = client.get("/advanced-analytics/filter?club=Liverpool")
    assert response.status_code == 200

    data = response.json()
    assert len(data) > 0
    assert all(player["club"] == "Liverpool" for player in data)


def test_scouting_targets(client, sample_players, sample_market_values):
    response = client.get(
        "/advanced-analytics/scouting-targets?min_minutes=900&max_value=50000000&min_performance=0"
    )
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)

    for player in data:
        assert player["market_value"] <= 50000000


def test_reliable_value_players(client, sample_players, sample_market_values):
    response = client.get(
        "/advanced-analytics/reliable-value-players"
        "?min_minutes=900&min_availability=0&min_performance=0&max_market_value=60000000&limit=10"
    )
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)

    for player in data:
        assert player["market_value_gbp"] <= 60000000
        assert player["performance_score"] >= 0
        assert "availability_factor" in player


def test_overvalued_players(client, sample_players, sample_market_values):
    response = client.get(
        "/advanced-analytics/overvalued-players"
        "?min_market_value=30000000&max_performance=1000&max_availability=1.0&limit=10"
    )
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)

    for player in data:
        assert player["market_value_gbp"] >= 30000000

def test_reliable_value_players_sorted(client, sample_players, sample_market_values):
    response = client.get(
        "/advanced-analytics/reliable-value-players"
        "?min_minutes=900&min_availability=0&min_performance=0&max_market_value=60000000&limit=10"
    )
    assert response.status_code == 200

    data = response.json()
    value_scores = [player["value_score"] for player in data]
    assert value_scores == sorted(value_scores, reverse=True)