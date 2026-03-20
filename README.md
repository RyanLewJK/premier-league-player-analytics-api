# ⚽ Premier League Player Analytics API

A FastAPI-based web service that provides advanced analytics on Premier League players by combining performance statistics with market valuation data.

---

## 📌 Overview

This project integrates two key datasets:

- 📊 **Player Performance Data** (goals, assists, minutes, defensive stats)
- 💰 **Estimated Transfer Value (ETV)** data

By combining these, the API generates advanced insights such as:

- Performance scores  
- Value-for-money analysis  
- Breakout player identification  

---

## 🚀 Features

### 🔹 Player CRUD
- Create, read, update, and delete player records

### 🔹 Market Value CRUD
- Manage player market values from cleaned ETV dataset

### 🔹 Analytics Endpoints

| Endpoint | Description |
|--------|------------|
| `/analytics/player-scores` | Full analytics for all players |
| `/analytics/top-performers` | Top players by performance score |
| `/analytics/best-value` | Players with best value for money |
| `/analytics/breakout-players` | High-performing players without market value |

---

## 🧠 Scoring System

### ⚡ Performance Score
Calculated using weighted per-90 metrics adjusted by player position:

- Goals and assists  
- Defensive contributions  
- Clean sheets  
- Discipline (cards)  
- Availability factor (minutes played)  

---

### 💰 Value Score
(performance_score × 1,000,000) / market_value_gbp
---

### 🌟 Breakout Score
Rewards high-performing players who do not yet have market value data.

---

## 🗂️ Project Structure

```bash
premier-league-player-analytics-api/
│
├── app/
│   ├── routers/
│   ├── models.py
│   ├── schemas.py
│   ├── scoring.py
│
├── scripts/
│   └── import_players_value.py
│
├── data/
│   ├── EPL_Player_Value.csv
│   └── cleaned_etv_player_values.csv
│
├── main.py
├── requirements.txt
└── README.md

## 📊 Data Sources

### Player Performance Data
- Fantasy Premier League dataset

### Market Value Data
- Estimated Transfer Value (ETV) dataset (manually collected)

---

## 🧹 Data Cleaning Pipeline

The ETV dataset required preprocessing due to inconsistent formatting.

Run the script:

```bash
python -m scripts.import_players_value

---

## 🔐 Authentication

This API implements **API key authentication** to protect sensitive endpoints.

### 🔒 Protected Endpoints

The following operations require authentication:

* `POST /players`
* `PUT /players/{id}`
* `PATCH /players/{id}`
* `DELETE /players/{id}`
* All `/market-values` write operations

### 🔑 How to Authenticate

Include the following header in your request:

```bash
X-API-Key: your-secret-key
```

### 🧪 Using Swagger UI

1. Open:

```bash
https://premier-league-player-analytics-api.onrender.com/docs
```

2. Click **Authorize 🔒**
3. Enter your API key
4. Execute protected endpoints

---

## 🌐 Deployment

The API is deployed using **Render**.

### ⚙️ Configuration

* **Platform:** Render
* **Runtime:** Python 3
* **Build Command:**

```bash
pip install -r requirements.txt
```

* **Start Command:**

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### 🔑 Environment Variables

| Variable  | Description                        |
| --------- | ---------------------------------- |
| `API_KEY` | Secret key for protected endpoints |

---

## 🗄️ Database Design & Initialization

The API uses **SQLite** as its database.

### Key Design Choices:

* Lightweight and easy to deploy
* Suitable for read-heavy analytics APIs
* No external database dependency required

### ⚠️ Important Note

The database file (`.db`) is **not stored in GitHub**.

Instead, the database is:

✔ Automatically created on startup
✔ Automatically populated from CSV datasets

This ensures:

* Consistent deployment
* No manual setup required
* Reproducibility across environments

---

## 🧪 Testing

The API includes a **comprehensive automated test suite** using `pytest`.

### Test Coverage

* ✅ Player CRUD endpoints
* ✅ Market value CRUD endpoints
* ✅ Analytics endpoints
* ✅ Advanced analytics endpoints
* ✅ Scoring functions

### Run tests locally:

```bash
pytest -v
```

### Result

All tests pass successfully, ensuring:

* Endpoint correctness
* Data integrity
* Accurate scoring logic

---

## 📈 Advanced Features

### 🧠 Analytics Engine

* Position-based scoring system
* League-wide normalization using z-scores
* Multi-factor evaluation (performance, value, availability)

### 🔍 Advanced Queries

* Player comparison
* Scouting targets
* Reliable value players
* Overvalued player detection

---

## 🔒 Security Considerations

* API key authentication for write operations
* Input validation via Pydantic schemas
* Controlled database access via dependency injection
* Separation of public and protected routes

---

## ⚠️ Limitations

* Uses static datasets (not real-time updates)
* SQLite not ideal for high-concurrency production systems
* Market value matching is name-based (may cause minor mismatches)

---

## 🚀 Future Improvements

* Real-time data integration (e.g. football-data API)
* PostgreSQL migration for scalability
* User authentication (JWT-based system)
* Rate limiting and request throttling
* Caching for analytics endpoints

---

## 👨‍💻 Author

Ryan Lew
Computer Science Student

---
