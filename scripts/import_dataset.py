from pathlib import Path
import pandas as pd

from app.database import SessionLocal, engine, Base
from app.models import Player


RAW_CSV_PATH = Path("data/fpl_player_statistics.csv")
CLEANED_CSV_PATH = Path("data/cleaned_fpl_player_statistics.csv")


COLUMNS_TO_KEEP = [
    "player_name",
    "club_name",
    "position_name",
    "minutes",
    "total_points",
    "points_per_game",
    "goals_scored",
    "assists",
    "clean_sheets",
    "goals_conceded",
    "saves",
    "defensive_contribution",
    "yellow_cards",
    "red_cards",
    "bonus",
]


NUMERIC_COLUMNS = [
    "minutes",
    "total_points",
    "points_per_game",
    "goals_scored",
    "assists",
    "clean_sheets",
    "goals_conceded",
    "saves",
    "defensive_contribution",
    "yellow_cards",
    "red_cards",
    "bonus",
]


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    missing_columns = [col for col in COLUMNS_TO_KEEP if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing expected columns: {missing_columns}")

    df = df[COLUMNS_TO_KEEP].copy()

    # Remove rows without core identity fields
    df = df.dropna(subset=["player_name", "club_name", "position_name"])

    # Standardize text fields
    df["player_name"] = df["player_name"].astype(str).str.strip()
    df["club_name"] = df["club_name"].astype(str).str.strip()
    df["position_name"] = df["position_name"].astype(str).str.strip().str.upper()

    # Keep only standard FPL positions if present
    valid_positions = {"GK", "DEF", "MID", "FWD"}
    df = df[df["position_name"].isin(valid_positions)]

    # Convert numeric columns safely
    for col in NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Cast integer-like columns cleanly
    int_columns = [
        "minutes",
        "total_points",
        "goals_scored",
        "assists",
        "clean_sheets",
        "goals_conceded",
        "saves",
        "defensive_contribution",
        "yellow_cards",
        "red_cards",
        "bonus",
    ]
    for col in int_columns:
        df[col] = df[col].astype(int)

    # Round points_per_game to 2 decimal places
    df["points_per_game"] = df["points_per_game"].round(2)

    # Optional filter: remove players with 0 minutes
    df = df[df["minutes"] > 0]

    # Remove exact duplicate rows if any
    df = df.drop_duplicates()

    # Sort nicely for consistency
    df = df.sort_values(
        by=["position_name", "total_points", "minutes"],
        ascending=[True, False, False]
    ).reset_index(drop=True)

    return df


def import_players_to_db(df: pd.DataFrame) -> None:
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Clear existing data so rerunning the script doesn't duplicate players
        db.query(Player).delete()
        db.commit()

        players = []
        for _, row in df.iterrows():
            players.append(
                Player(
                    player_name=row["player_name"],
                    club_name=row["club_name"],
                    position_name=row["position_name"],
                    minutes=row["minutes"],
                    total_points=row["total_points"],
                    points_per_game=row["points_per_game"],
                    goals_scored=row["goals_scored"],
                    assists=row["assists"],
                    clean_sheets=row["clean_sheets"],
                    goals_conceded=row["goals_conceded"],
                    saves=row["saves"],
                    defensive_contribution=row["defensive_contribution"],
                    yellow_cards=row["yellow_cards"],
                    red_cards=row["red_cards"],
                    bonus=row["bonus"],
                )
            )

        db.bulk_save_objects(players)
        db.commit()

        print(f"Imported {len(players)} players into the database.")
    finally:
        db.close()


def main() -> None:
    if not RAW_CSV_PATH.exists():
        raise FileNotFoundError(
            f"Could not find dataset at '{RAW_CSV_PATH}'. "
            "Place the CSV file in the data folder."
        )

    raw_df = pd.read_csv(RAW_CSV_PATH)
    cleaned_df = clean_dataframe(raw_df)

    # Save cleaned CSV for transparency/debugging
    CLEANED_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    cleaned_df.to_csv(CLEANED_CSV_PATH, index=False)

    print("Cleaned dataset saved to:", CLEANED_CSV_PATH)
    print("Rows after cleaning:", len(cleaned_df))
    print("Columns kept:", list(cleaned_df.columns))

    import_players_to_db(cleaned_df)


if __name__ == "__main__":
    main()