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

def fetch_teams():
    headers = {"X-Auth-Token": FOOTBALL_API_KEY}
    
    response = requests.get(
        f"{BASE_URL}/competitions/WC/teams",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"API error: {response.status_code}")
        print(response.json())
        return
    
    data = response.json()
    teams = data["teams"]
    print(f"Fetched {len(teams)} teams from API")
    
    supabase = get_supabase()
    
    for team in teams:
        team_data = {
            "api_id": team["id"],
            "name": team["name"],
            "short_name": team["shortName"],
            "crest_url": team["crest"]
        }
        
        supabase.table("teams").upsert(
            team_data,
            on_conflict="api_id"
        ).execute()
    
    print(f"Successfully inserted {len(teams)} teams into database")

if __name__ == "__main__":
    fetch_teams()