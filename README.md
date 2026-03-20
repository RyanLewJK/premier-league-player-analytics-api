# ⚽ Premier League Player Analytics API

A FastAPI-based web service that provides advanced analytics on Premier League players by combining performance statistics with market valuation data.

---

## 📌 Overview

This project integrates two key datasets:

- 📊 **Player Performance Data** (goals, assists, minutes, defensive stats)
- 💰 **Estimated Transfer Value (ETV)** data

By combining these datasets, the API generates meaningful insights such as:

- Performance scoring
- Value-for-money analysis
- Breakout player identification

The system supports both **CRUD operations** and **advanced analytics**, making it suitable for data-driven football analysis.

---

## 🚀 Features

### 🔹 Player CRUD
- Create, read, update, and delete player records

### 🔹 Market Value CRUD
- Manage player market value records

### 🔹 Analytics
- Performance scoring
- Best-value player identification
- Breakout player detection

### 🔹 Advanced Analytics
- Player comparison
- Scouting target identification
- Reliable value player detection
- Overvalued player analysis

---

## 📌 Example Usage

### Request
```http
GET https://premier-league-player-analytics-api.onrender.com/analytics/top-performers?limit=3
```

### Example Response
```json
[
  {
    "player_name": "Erling Haaland",
    "performance_score": 95.3
  },
  {
    "player_name": "Bukayo Saka",
    "performance_score": 92.7
  }
]
```
## 🧩 System Overview

The API processes data using the following pipeline:

CSV datasets → Data cleaning scripts → SQLite database → FastAPI endpoints → Analytics calculations → JSON response

This design separates data ingestion from runtime analytics, improving maintainability and scalability.

---
## 🌐 Accessing the API

The deployed API is available at:

`https://premier-league-player-analytics-api.onrender.com`

Interactive Swagger documentation:

`https://premier-league-player-analytics-api.onrender.com/docs`

This allows endpoints to be tested directly in the browser without local setup.

---

## ⚙️ Local Setup Instructions

Follow these steps to run the API locally on your machine.

---

### 1. Clone the Repository

```bash
git clone https://github.com/RyanLewJK/premier-league-player-analytics-api.git
cd premier-league-player-analytics-api
```

---

### 2. Create a Virtual Environment

#### macOS / Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Set Environment Variables

Create a `.env` file in the root directory (optional but recommended):

```env
API_KEY=your-secret-key
```

Or set it in your terminal:

#### macOS / Linux
```bash
export API_KEY=your-secret-key
```

#### Windows (PowerShell)
```bash
setx API_KEY "your-secret-key"
```

---

### 5. Initialise the Database

Run the import script to populate the database with player and market value data:

```bash
python -m scripts.import_dataset
python -m scripts.import_players_value
```

---

### 6. Run the API

```bash
uvicorn app.main:app --reload
```

---

### 7. Access the API

- API Base URL:  
  `http://127.0.0.1:8000`

- Swagger UI (interactive documentation):  
  `http://127.0.0.1:8000/docs`

---

### 8. Using Authentication Locally

For protected endpoints, include the API key in your request header:

```bash
X-API-Key: your-secret-key
```

---

### Notes

- The database is automatically created on first run  
- The import script must be executed to populate data  
- Without running the script, analytics endpoints may return empty results  

---

## 🔐 Authentication

This API uses **API key authentication** to protect write operations.

### 🔒 Protected Endpoints
Authentication is required for:
- `POST /players`
- `PUT /players/{player_id}`
- `PATCH /players/{player_id}`
- `DELETE /players/{player_id}`
- `POST /market-values`
- `PUT /market-values/{market_value_id}`
- `PATCH /market-values/{market_value_id}`
- `DELETE /market-values/{market_value_id}`

### 🔓 Public Endpoints
All `GET` endpoints are publicly accessible.

### 🔑 Header Format

```bash
X-API-Key: your-api-key-here
```

For security reasons, the API key is not published in this repository, it is however in the technical report submitted in the coursework (within the appendix section).

---

## 🧠 Scoring System

### ⚡ Performance Score
Calculated using weighted per-90 metrics adjusted by player position:

- Goals and assists
- Defensive contributions
- Clean sheets
- Discipline (cards)
- Availability factor (minutes played)

### 💰 Value Score

```text
(performance_score × 1,000,000) / market_value_gbp
```

### 🌟 Breakout Score
Rewards high-performing players who do not yet have market value data.

---

## 🗂️ Project Structure

```bash
premier-league-player-analytics-api/
│
├── app/
│   ├── routers/
│   │   ├── players.py
│   │   ├── market_values.py
│   │   ├── analytics.py
│   │   └── advanced_analytics.py
│   │
│   ├── models.py
│   ├── schemas.py
│   ├── scoring.py
│   ├── security.py
│   ├── database.py
│   └── main.py
│
├── data/
│   ├── cleaned_etv_player_values.csv
│   ├── cleaned_fpl_player_statistics.csv
│   ├── EPL_Player_Value.csv
│   └── fpl_player_statistics.csv
│
├── scripts/
│   ├── import_dataset.py
│   └── import_players_value.py
│
├── tests/
│   ├── conftest.py
│   ├── test_players_api.py
│   ├── test_market_values_api.py
│   ├── test_analytics_api.py
│   ├── test_advanced_analytics_api.py
│   └── test_scoring.py
│
├── docs/
│   └── api-documentation.pdf
│
├── requirements.txt
├── README.md
└── LICENSE
```
---

## 📊 Data Sources

### Player Performance Data
- Fantasy Premier League dataset

### Market Value Data
- Estimated Transfer Value (ETV) dataset, manually collected and cleaned

---

## 🧹 Data Cleaning Pipeline

The ETV dataset required preprocessing due to inconsistent formatting.

Run the import script using:

```bash
python -m scripts.import_players_value
```

This script cleans and normalises the market value data before inserting it into the database.

---

## 🗄️ Database Design & Initialization

The API uses **SQLite** as its database.

### Key Design Choices
- Lightweight and easy to deploy
- Suitable for read-heavy analytics APIs
- No external database dependency required

### Important Note

The database file (`.db`) is not stored in GitHub.

Instead, the database is:

- Automatically created on startup
- Automatically populated from CSV datasets

This ensures:

- Consistent deployment
- No manual setup required
- Reproducibility across environments

This choice aligns with the project’s focus on simplicity, reproducibility, and read-heavy analytical workloads rather than high-concurrency production use.

---

## 🌐 Deployment

The API is deployed using **Render**.

### ⚙️ Configuration

- **Platform:** Render
- **Runtime:** Python 3

**Build Command:**

```bash
pip install -r requirements.txt
```

**Start Command:**

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### 🔑 Environment Variables

| Variable | Description |
|---|---|
| `API_KEY` | Secret key for protected endpoints |

---

## 🧪 Testing

The API includes a comprehensive automated test suite using `pytest`.

### Test Coverage
- Player CRUD endpoints
- Market value CRUD endpoints
- Analytics endpoints
- Advanced analytics endpoints
- Scoring functions

### Run tests locally

```bash
pytest -v
```

All tests pass successfully, ensuring correctness and reliability.

---

## 📈 Advanced Features

### 🧠 Analytics Engine
- Position-based scoring system
- League-wide normalisation using z-scores
- Multi-factor evaluation using performance, value, and availability

### 🔍 Advanced Queries
- Player comparison
- Scouting targets
- Reliable value players
- Overvalued player detection

---

## 🔒 Security Considerations

- API key authentication for write operations
- Input validation using Pydantic schemas
- Controlled database access via dependency injection
- Separation of public and protected endpoints

---

## ⚠️ Limitations

- Uses static datasets rather than real-time updates
- SQLite is not suitable for high-concurrency production systems
- Market value matching is name-based and may introduce minor inconsistencies

---

## 🚀 Future Improvements

- Real-time data integration using football data APIs
- Migration to PostgreSQL for scalability
- JWT-based user authentication
- Rate limiting and request throttling
- Caching for analytics endpoints

---

## 📄 API Documentation

The full API documentation is available here:

[View API Documentation](docs/Premier%20League%20Player%20Analytics%20API%20documentation.pdf)

Swagger UI endpoints examples also available:

[Swagger UI](docs/Premier%20League%20Player%20Analytics%20API%20-%20Swagger%20UI.pdf)

---

## 📚 Sources

- [Fantasy Premier League](https://www.kaggle.com/datasets/calvinrostanto/fantasy-premier-league-2025-2026)
- [Estimated Transfer Value ETV dataset](https://www.footballtransfers.com/en/values/players/most-valuable-players/playing-in-uk-premier-league)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Render Documentation](https://render.com/docs)

Full academic references are included in the technical report.

---

## 🤖 AI Declaration

AI-based tools were used during the development of this project to support drafting, refinement, and explanation of implementation details. All design decisions, implementation, testing, and final submitted content were reviewed and validated by the author.

---

## 👨‍💻 Author

**Ryan Lew**  
Computer Science Student