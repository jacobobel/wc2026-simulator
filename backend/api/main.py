import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

load_dotenv()

app = FastAPI(title="WC2026 Simulator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_supabase():
    return create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_KEY")
    )

@app.get("/")
def root():
    return {"status": "WC2026 Simulator API running"}

@app.get("/teams")
def get_teams():
    supabase = get_supabase()
    result = supabase.table("teams")\
        .select("*, team_ratings(*), simulation_results(*)")\
        .order("name")\
        .execute()
    return result.data

@app.get("/teams/{team_name}")
def get_team(team_name: str):
    supabase = get_supabase()
    result = supabase.table("teams")\
        .select("*, team_ratings(*), simulation_results(*)")\
        .eq("name", team_name)\
        .execute()
    if not result.data:
        return {"error": "Team not found"}
    return result.data[0]

@app.get("/standings")
def get_standings():
    supabase = get_supabase()
    result = supabase.table("teams")\
        .select("name, group_name, simulation_results(win_pct, final_pct, semi_pct, quarter_pct, r32_pct, group_exit_pct)")\
        .order("group_name")\
        .execute()
    return result.data

@app.get("/simulate/{team_a}/{team_b}")
def simulate_match(team_a: str, team_b: str):
    supabase = get_supabase()

    result = supabase.table("team_ratings")\
        .select("*, team:team_id(name)")\
        .execute()
    all_ratings = {r["team"]["name"]: r for r in result.data if r.get("team")}

    if team_a not in all_ratings:
        return {"error": f"Team not found: {team_a}"}
    if team_b not in all_ratings:
        return {"error": f"Team not found: {team_b}"}

    config = supabase.table("config").select("value").eq("key", "global_avg_goals").execute()
    avg_goals = config.data[0]["value"] if config.data else 1.5

    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from simulation.poisson import simulate_match as run_simulation

    result = run_simulation(all_ratings[team_a], all_ratings[team_b], avg_goals=avg_goals)
    return {
        "team_a": team_a,
        "team_b": team_b,
        "prob_a_wins": result["prob_a_wins"],
        "prob_draw": result["prob_draw"],
        "prob_b_wins": result["prob_b_wins"],
        "expected_goals_a": result["expected_goals_a"],
        "expected_goals_b": result["expected_goals_b"],
        "most_likely_score": result["most_likely_score"]
    }

@app.get("/odds")
def get_odds():
    supabase = get_supabase()
    result = supabase.table("simulation_results")\
        .select("*, team:team_id(name, group_name, crest_url)")\
        .order("win_pct", desc=True)\
        .execute()
    return result.data

@app.get("/groups")
def get_groups():
    supabase = get_supabase()
    result = supabase.table("teams")\
        .select("name, group_name, crest_url, simulation_results(win_pct, r32_pct, group_exit_pct)")\
        .order("group_name")\
        .execute()

    groups = {}
    for team in result.data:
        group = team["group_name"] or "Unknown"
        if group not in groups:
            groups[group] = []
        groups[group].append(team)

    return groups

# Serve React frontend
frontend_build = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "frontend", "dist"
)

if os.path.exists(frontend_build):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_build, "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_frontend(full_path: str):
        index = os.path.join(frontend_build, "index.html")
        return FileResponse(index)