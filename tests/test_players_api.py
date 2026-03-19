def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Premier League Player Analytics API is running"}


def test_create_player(client):
    payload = {
        "player_name": "Bukayo Saka",
        "club_name": "Arsenal",
        "position_name": "MID",
        "minutes": 2700,
        "total_points": 200,
        "points_per_game": 6.4,
        "goals_scored": 14,
        "assists": 11,
        "clean_sheets": 10,
        "goals_conceded": 32,
        "saves": 0,
        "defensive_contribution": 18,
        "yellow_cards": 5,
        "red_cards": 0,
        "bonus": 17
    }

    response = client.post("/players", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["player_name"] == "Bukayo Saka"
    assert data["club_name"] == "Arsenal"
    assert "id" in data


def test_get_all_players(client, sample_players):
    response = client.get("/players")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 5


def test_get_player_by_id(client, sample_players):
    player_id = sample_players[0].id

    response = client.get(f"/players/{player_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["player_name"] == "Mohamed Salah"


def test_get_player_not_found(client):
    response = client.get("/players/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Player not found"


def test_search_players(client, sample_players):
    response = client.get("/players/search?name=salah")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["player_name"] == "Mohamed Salah"


def test_get_players_by_position(client, sample_players):
    response = client.get("/players/position/MID")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    assert all(player["position_name"] == "MID" for player in data)


def test_get_players_by_club(client, sample_players):
    response = client.get("/players/club/Liverpool")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    assert all(player["club_name"] == "Liverpool" for player in data)


def test_put_update_player(client, sample_players):
    player_id = sample_players[0].id

    payload = {
        "player_name": "Mohamed Salah Updated",
        "club_name": "Liverpool",
        "position_name": "MID",
        "minutes": 2850,
        "total_points": 245,
        "points_per_game": 7.7,
        "goals_scored": 19,
        "assists": 11,
        "clean_sheets": 12,
        "goals_conceded": 30,
        "saves": 0,
        "defensive_contribution": 21,
        "yellow_cards": 2,
        "red_cards": 0,
        "bonus": 26
    }

    response = client.put(f"/players/{player_id}", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["player_name"] == "Mohamed Salah Updated"
    assert data["minutes"] == 2850


def test_patch_player(client, sample_players):
    player_id = sample_players[1].id

    response = client.patch(f"/players/{player_id}", json={"minutes": 2600})
    assert response.status_code == 200

    data = response.json()
    assert data["player_name"] == "Cole Palmer"
    assert data["minutes"] == 2600


def test_delete_player(client, sample_players):
    player_id = sample_players[2].id

    response = client.delete(f"/players/{player_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Player deleted successfully"

    get_response = client.get(f"/players/{player_id}")
    assert get_response.status_code == 404