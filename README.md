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