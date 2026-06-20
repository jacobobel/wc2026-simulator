import os
import csv
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def get_supabase():
    return create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_KEY")
    )

def load_csv_to_db(filepath):
    supabase = get_supabase()
    inserted = 0
    skipped = 0

    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                match_data = {
                    "home_team": row["home_team"],
                    "away_team": row["away_team"],
                    "home_score": int(row["home_score"]),
                    "away_score": int(row["away_score"]),
                    "match_date": row["match_date"],
                    "confederation": row["confederation"],
                    "tournament": row["tournament"],
                    "tournament_stage": row["tournament_stage"],
                    "home_team_fifa_ranking": int(row["home_team_fifa_ranking"]) if row["home_team_fifa_ranking"] else None,
                    "away_team_fifa_ranking": int(row["away_team_fifa_ranking"]) if row["away_team_fifa_ranking"] else None,
                }
                supabase.table("competitive_matches").upsert(
                    match_data,
                    on_conflict="home_team,away_team,match_date"
                ).execute()
                inserted += 1
            except Exception as e:
                print(f"Error: {row['home_team']} vs {row['away_team']}: {e}")
                skipped += 1

    print(f"Done — inserted {inserted}, skipped {skipped}")

if __name__ == "__main__":
    load_csv_to_db("backend/data/afcon_2025.csv")