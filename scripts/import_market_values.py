from pathlib import Path
import pandas as pd

from app.database import SessionLocal, engine, Base
from app.models import PlayerMarketValue


RAW_CSV_PATH = Path("data/transfermarkt_player_values.csv")
CLEANED_CSV_PATH = Path("data/cleaned_transfermarkt_player_values.csv")

EUR_TO_GBP = 0.86

COLUMNS_TO_KEEP = [
    "name",
    "age",
    "position",
    "position_group",
    "current_club",
    "league_name",
    "current_value_eur",
    "peak_value_eur",
    "trajectory",
]


def normalize_text(value: str) -> str:
    return str(value).strip().lower()


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    missing_columns = [col for col in COLUMNS_TO_KEEP if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing expected columns: {missing_columns}")

    df = df[COLUMNS_TO_KEEP].copy()

    df = df[df["league_name"].astype(str).str.strip().str.lower() == "premier league"]
    df = df.dropna(subset=["name", "current_club"])

    df = df.rename(columns={
        "name": "player_name",
        "current_club": "club_name"
    })

    df["player_name"] = df["player_name"].astype(str).str.strip()
    df["club_name"] = df["club_name"].astype(str).str.strip()
    df["league_name"] = df["league_name"].astype(str).str.strip()

    df["normalized_name"] = df["player_name"].apply(normalize_text)
    df["normalized_club"] = df["club_name"].apply(normalize_text)

    for col in ["position", "position_group", "trajectory"]:
        df[col] = df[col].fillna("").astype(str).str.strip()

    for col in ["age", "current_value_eur", "peak_value_eur"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["age"] = df["age"].astype(int)
    df["current_value_gbp"] = (df["current_value_eur"] * EUR_TO_GBP).round(2)
    df["peak_value_gbp"] = (df["peak_value_eur"] * EUR_TO_GBP).round(2)

    df = df.drop(columns=["current_value_eur", "peak_value_eur"])
    df = df.drop_duplicates(subset=["normalized_name", "normalized_club"])
    df = df.sort_values(by=["current_value_gbp", "player_name"], ascending=[False, True]).reset_index(drop=True)

    return df


def import_market_values_to_db(df: pd.DataFrame) -> None:
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        db.query(PlayerMarketValue).delete()
        db.commit()

        rows = []
        for _, row in df.iterrows():
            rows.append(
                PlayerMarketValue(
                    player_name=row["player_name"],
                    normalized_name=row["normalized_name"],
                    club_name=row["club_name"],
                    normalized_club=row["normalized_club"],
                    age=row["age"],
                    position=row["position"],
                    position_group=row["position_group"],
                    league_name=row["league_name"],
                    current_value_gbp=row["current_value_gbp"],
                    peak_value_gbp=row["peak_value_gbp"],
                    trajectory=row["trajectory"],
                )
            )

        db.bulk_save_objects(rows)
        db.commit()
        print(f"Imported {len(rows)} market value rows.")
    finally:
        db.close()


def main():
    if not RAW_CSV_PATH.exists():
        raise FileNotFoundError(
            f"Could not find dataset at '{RAW_CSV_PATH}'. Place the CSV in the data folder."
        )

    raw_df = pd.read_csv(RAW_CSV_PATH)
    cleaned_df = clean_dataframe(raw_df)

    CLEANED_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    cleaned_df.to_csv(CLEANED_CSV_PATH, index=False)

    print("Saved cleaned market value dataset to:", CLEANED_CSV_PATH)
    print("Rows after cleaning:", len(cleaned_df))

    import_market_values_to_db(cleaned_df)


if __name__ == "__main__":
    main()