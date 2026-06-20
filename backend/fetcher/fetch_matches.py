import os
import requests
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

FOOTBALL_API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
BASE_URL = "https://api.football-data.org/v4"

def get_supabase():
    return create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_KEY")
    )

def get_team_db_id(supabase, api_id):
    result = supabase.table("teams").select("id").eq("api_id", api_id).execute()
    if result.data:
        return result.data[0]["id"]
    return None

def fetch_matches():
    headers = {"X-Auth-Token": FOOTBALL_API_KEY}
    
    response = requests.get(
        f"{BASE_URL}/competitions/WC/matches",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"API error: {response.status_code}")
        print(response.json())
        return
    
    data = response.json()
    matches = data["matches"]
    print(f"Fetched {len(matches)} matches from API")
    
    supabase = get_supabase()
    inserted = 0
    skipped = 0
    
    for match in matches:
        home_api_id = match["homeTeam"]["id"]
        away_api_id = match["awayTeam"]["id"]
        
        # Skip matches where teams aren't determined yet
        if not home_api_id or not away_api_id:
            skipped += 1
            continue
        
        home_db_id = get_team_db_id(supabase, home_api_id)
        away_db_id = get_team_db_id(supabase, away_api_id)
        
        if not home_db_id or not away_db_id:
            print(f"Skipping match {match['id']} - team not found in DB")
            skipped += 1
            continue
        
        score = match["score"]["fullTime"]
        
        match_data = {
            "api_id": match["id"],
            "home_team_id": home_db_id,
            "away_team_id": away_db_id,
            "home_score": score["home"],
            "away_score": score["away"],
            "stage": match["stage"],
            "group_name": match.get("group"),
            "match_date": match["utcDate"],
            "status": match["status"]
        }
        
        supabase.table("matches").upsert(
            match_data,
            on_conflict="api_id"
        ).execute()
        inserted += 1
    
    print(f"Successfully inserted {inserted} matches, skipped {skipped}")

if __name__ == "__main__":
    fetch_matches()