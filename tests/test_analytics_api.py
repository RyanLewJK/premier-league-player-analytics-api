def test_get_player_scores(client, sample_players, sample_market_values):
    response = client.get("/analytics/player-scores")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 5

    salah = next(player for player in data if player["player_name"] == "Mohamed Salah")
    prospect = next(player for player in data if player["player_name"] == "Young Prospect")

    assert salah["market_value_gbp"] is not None
    assert salah["value_score"] is not None

    assert prospect["market_value_gbp"] is None
    assert prospect["breakout_score"] is not None


def test_top_performers_limit(client, sample_players, sample_market_values):
    response = client.get("/analytics/top-performers?limit=3")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 3

    scores = [player["performance_score"] for player in data]
    assert scores == sorted(scores, reverse=True)


def test_best_value_returns_only_players_with_market_values(client, sample_players, sample_market_values):
    response = client.get("/analytics/best-value")
    assert response.status_code == 200

    data = response.json()
    assert len(data) > 0
    assert all(player["value_score"] is not None for player in data)
    assert all(player["market_value_gbp"] is not None for player in data)


def test_breakout_players_returns_players_without_market_values(client, sample_players, sample_market_values):
    response = client.get("/analytics/breakout-players")
    assert response.status_code == 200

    data = response.json()
    assert len(data) > 0
    assert all(player["breakout_score"] is not None for player in data)
    assert all(player["market_value_gbp"] is None for player in data)


def test_best_value_by_position(client, sample_players, sample_market_values):
    response = client.get("/analytics/best-value/MID?limit=5")
    assert response.status_code == 200

    data = response.json()
    assert all(player["position_name"] == "MID" for player in data)


def test_best_value_by_position_invalid_position(client, sample_players, sample_market_values):
    response = client.get("/analytics/best-value/XYZ")
    assert response.status_code == 400
    assert "Invalid position" in response.json()["detail"]


def test_top_performers_by_position_with_min_minutes(client, sample_players, sample_market_values):
    response = client.get("/analytics/top-performers/MID?min_minutes=2600")
    assert response.status_code == 200

    data = response.json()
    assert all(player["position_name"] == "MID" for player in data)
    assert all(player["minutes"] >= 2600 for player in data)


def test_best_value_sorted_descending(client, sample_players, sample_market_values):
    response = client.get("/analytics/best-value?limit=10")
    assert response.status_code == 200

    data = response.json()
    scores = [player["value_score"] for player in data]
    assert scores == sorted(scores, reverse=True)



def test_breakout_players_sorted_descending(client, sample_players, sample_market_values):
    response = client.get("/analytics/breakout-players?limit=10")
    assert response.status_code == 200

    data = response.json()
    scores = [player["breakout_score"] for player in data]
    assert scores == sorted(scores, reverse=True)