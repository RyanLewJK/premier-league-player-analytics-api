from pathlib import Path
import re
import pandas as pd

from app.database import SessionLocal, engine, Base
from app.models import PlayerMarketValue


RAW_CSV_PATH = Path("data/EPL_Player_Value.csv")
CLEANED_CSV_PATH = Path("data/cleaned_etv_player_values.csv")

EUR_TO_GBP = 0.86


def normalize_text(value: str) -> str:
    return str(value).strip().lower()


def clean_player_name(value: str) -> str:
    if pd.isna(value):
        return ""

    name = str(value).strip().replace("\xa0", " ")

    match = re.match(
        r"^(.*?)(?=(?:GK|CB|LB|RB|WB|DM|CM|AM|LM|RM|LW|RW|SS|CF|ST|F|M|D)(?:,|\s*\(|$))",
        name
    )

    if match:
        return match.group(1).strip()

    return name


def parse_etv_to_gbp(value: str) -> float:
    if pd.isna(value):
        return 0.0

    text = str(value).strip().replace("€", "").replace(",", "")

    if not text:
        return 0.0

    multiplier = 1

    if text.endswith("M"):
        multiplier = 1_000_000
        text = text[:-1]
    elif text.endswith("K"):
        multiplier = 1_000
        text = text[:-1]
    elif text.endswith("B"):
        multiplier = 1_000_000_000
        text = text[:-1]

    try:
        eur_value = float(text) * multiplier
        gbp_value = eur_value * EUR_TO_GBP
        return round(gbp_value, 2)
    except ValueError:
        return 0.0


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    required_columns = ["Player", "ETV"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing expected columns: {missing_columns}")

    df = df.dropna(how="all").reset_index(drop=True)

    cleaned_rows = []

    i = 0
    while i < len(df) - 1:
        current_row = df.iloc[i]

        if pd.notna(current_row["ETV"]):
            next_row = df.iloc[i + 1]

            player_name = clean_player_name(next_row["Player"])
            current_value_gbp = parse_etv_to_gbp(current_row["ETV"])

            if player_name:
                cleaned_rows.append({
                    "player_name": player_name,
                    "normalized_name": normalize_text(player_name),
                    "club_name": "",
                    "normalized_club": "",
                    "age": 0,
                    "position": "",
                    "position_group": "",
                    "league_name": "Premier League",
                    "current_value_gbp": current_value_gbp,
                    "peak_value_gbp": current_value_gbp,
                    "trajectory": "",
                })

            i += 2
        else:
            i += 1

    cleaned_df = pd.DataFrame(cleaned_rows)

    cleaned_df = cleaned_df.drop_duplicates(subset=["normalized_name"])
    cleaned_df = cleaned_df.sort_values(
        by=["current_value_gbp", "player_name"],
        ascending=[False, True]
    ).reset_index(drop=True)

    return cleaned_df


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
                    age=int(row["age"]),
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

    raw_df = pd.read_csv(RAW_CSV_PATH, encoding="cp1252")
    cleaned_df = clean_dataframe(raw_df)

    CLEANED_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    cleaned_df.to_csv(CLEANED_CSV_PATH, index=False)

    print("Saved cleaned market value dataset to:", CLEANED_CSV_PATH)
    print("Rows after cleaning:", len(cleaned_df))

    import_market_values_to_db(cleaned_df)


if __name__ == "__main__":
    main()