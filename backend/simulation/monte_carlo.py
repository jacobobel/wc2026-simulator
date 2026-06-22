import os
import sys
import math
import random
from dotenv import load_dotenv
from supabase import create_client

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from poisson import simulate_match

load_dotenv()

def get_supabase():
    return create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_KEY")
    )

GROUPS = {
    "A": ["Mexico", "South Korea", "Czechia", "South Africa"],
    "B": ["Canada", "Switzerland", "Bosnia-Herzegovina", "Qatar"],
    "C": ["Brazil", "Morocco", "Scotland", "Haiti"],
    "D": ["United States", "Australia", "Turkey", "Paraguay"],
    "E": ["Germany", "Curaçao", "Ivory Coast", "Ecuador"],
    "F": ["Japan", "Netherlands", "Tunisia", "Sweden"],
    "G": ["Belgium", "Iran", "New Zealand", "Egypt"],
    "H": ["Spain", "Cape Verde Islands", "Saudi Arabia", "Uruguay"],
    "I": ["France", "Senegal", "Iraq", "Norway"],
    "J": ["Argentina", "Algeria", "Austria", "Jordan"],
    "K": ["Portugal", "Colombia", "Congo DR", "Uzbekistan"],
    "L": ["England", "Croatia", "Ghana", "Panama"]
}

def load_played_results(supabase):
    result = supabase.table("matches")\
        .select("*, home:home_team_id(name), away:away_team_id(name)")\
        .eq("status", "FINISHED")\
        .execute()

    played = {}
    for m in result.data:
        if m.get("home") and m.get("away"):
            home = m["home"]["name"]
            away = m["away"]["name"]
            played[(home, away)] = (m["home_score"], m["away_score"])

    return played

def update_standings(standings, home, away, hg, ag):
    standings[home]["gf"] += hg
    standings[home]["ga"] += ag
    standings[home]["gd"] += hg - ag
    standings[home]["played"] += 1
    standings[away]["gf"] += ag
    standings[away]["ga"] += hg
    standings[away]["gd"] += ag - hg
    standings[away]["played"] += 1

    if hg > ag:
        standings[home]["pts"] += 3
    elif hg == ag:
        standings[home]["pts"] += 1
        standings[away]["pts"] += 1
    else:
        standings[away]["pts"] += 3

def simulate_single_match(ratings_a, ratings_b, avg_goals):
    result = simulate_match(ratings_a, ratings_b, avg_goals=avg_goals)

    score_matrix = result["score_matrix"]
    scores = list(score_matrix.keys())
    probs = list(score_matrix.values())

    total = sum(probs)
    probs = [p / total for p in probs]

    chosen = random.choices(scores, weights=probs, k=1)[0]
    parts = chosen.split("-")
    return int(parts[0]), int(parts[1])

def get_group_standings(group_name, teams, all_ratings, played_results, avg_goals, simulate_remaining=True):
    standings = {team: {"pts": 0, "gf": 0, "ga": 0, "gd": 0, "played": 0} for team in teams}

    for i in range(len(teams)):
        for j in range(i + 1, len(teams)):
            home = teams[i]
            away = teams[j]

            result = played_results.get((home, away)) or played_results.get((away, home))

            if result:
                if played_results.get((home, away)):
                    hg, ag = result
                else:
                    ag, hg = result
                update_standings(standings, home, away, hg, ag)

            elif simulate_remaining:
                if home in all_ratings and away in all_ratings:
                    hg, ag = simulate_single_match(all_ratings[home], all_ratings[away], avg_goals)
                    update_standings(standings, home, away, hg, ag)

    return standings

def rank_teams(standings):
    teams = list(standings.keys())
    teams.sort(key=lambda t: (
        -standings[t]["pts"],
        -standings[t]["gd"],
        -standings[t]["gf"]
    ))
    return teams

def simulate_knockout_match(team_a, team_b, all_ratings, avg_goals):
    if team_a not in all_ratings or team_b not in all_ratings:
        return random.choice([team_a, team_b])

    hg, ag = simulate_single_match(all_ratings[team_a], all_ratings[team_b], avg_goals)

    if hg > ag:
        return team_a
    elif ag > hg:
        return team_b
    else:
        rating_a = all_ratings[team_a]["composite_rating"]
        rating_b = all_ratings[team_b]["composite_rating"]
        prob_a = rating_a / (rating_a + rating_b)
        return team_a if random.random() < prob_a else team_b

def build_r32_bracket(group_results, third_place_teams):
    w = {g: group_results[g][0] for g in GROUPS}
    r = {g: group_results[g][1] for g in GROUPS}

    # Best 8 third place teams
    best_third = [t["team"] for t in sorted(
        third_place_teams,
        key=lambda x: (-x["pts"], -x["gd"], -x["gf"])
    )[:8]]

    # Fixed R32 matchups — runners-up vs runners-up, winners vs runners-up
    # Based on FIFA's predetermined bracket structure
    r32 = [
        # Left side of bracket
        (w["A"], best_third[0]),   # M79: 1A vs best 3rd (CEFHI)
        (r["A"], r["B"]),          # M73: 2A vs 2B
        (w["C"], r["F"]),          # M76: 1C vs 2F
        (w["F"], r["C"]),          # M75: 1F vs 2C
        (w["E"], best_third[1]),   # M74: 1E vs best 3rd (ABCDF)
        (r["E"], r["I"]),          # M78: 2E vs 2I
        (w["I"], best_third[2]),   # M77: 1I vs best 3rd (CDFGH)
        (w["B"], best_third[3]),   # M81: 1B vs best 3rd (EFGIJ)

        # Right side of bracket
        (w["H"], r["J"]),          # M84: 1H vs 2J
        (w["J"], r["H"]),          # M83: 1J vs 2H
        (w["G"], best_third[4]),   # M82: 1G vs best 3rd (AEHIJ)
        (r["D"], r["G"]),          # M85: 2D vs 2G
        (w["D"], best_third[5]),   # M86: 1D vs best 3rd (DEJL)
        (w["K"], best_third[6]),   # M87: 1K vs best 3rd (DEIJL)
        (r["K"], r["L"]),          # M88: 2K vs 2L
        (w["L"], best_third[7]),   # M80: 1L vs best 3rd (EHIJK)
    ]

    return r32

def simulate_tournament(all_ratings, supabase, n_simulations=10000):
    played_results = load_played_results(supabase)
    print(f"Loaded {len(played_results)} completed matches from database")

    config = supabase.table("config").select("value").eq("key", "global_avg_goals").execute()
    avg_goals = config.data[0]["value"] if config.data else 1.5
    print(f"Global average goals: {avg_goals:.4f}")

    stats = {team: {
        "r32": 0, "r16": 0, "qf": 0, "sf": 0, "final": 0, "winner": 0
    } for teams in GROUPS.values() for team in teams}

    for sim in range(n_simulations):
        group_results = {}
        third_place_teams = []

        # Simulate group stage
        for group_name, teams in GROUPS.items():
            standings = get_group_standings(
                group_name, teams, all_ratings, played_results, avg_goals
            )
            ranked = rank_teams(standings)
            group_results[group_name] = ranked

            third_place_teams.append({
                "team": ranked[2],
                "group": group_name,
                "pts": standings[ranked[2]]["pts"],
                "gd": standings[ranked[2]]["gd"],
                "gf": standings[ranked[2]]["gf"]
            })

        # Build R32 bracket using real FIFA structure
        r32_matches = build_r32_bracket(group_results, third_place_teams)

        # Track R32 participants
        for home, away in r32_matches:
            if home in stats: stats[home]["r32"] += 1
            if away in stats: stats[away]["r32"] += 1

        # Simulate R32 — 16 matches → 16 winners
        r16_teams = []
        for home, away in r32_matches:
            winner = simulate_knockout_match(home, away, all_ratings, avg_goals)
            r16_teams.append(winner)

        # R16 bracket — winners of adjacent R32 matches play each other
        # M73 winner vs M75 winner, M74 winner vs M76 winner etc.
        # Left side: matches 0-7 → R16 matches paired as (0v1, 2v3, 4v5, 6v7)
        # Right side: matches 8-15 → R16 matches paired as (8v9, 10v11, 12v13, 14v15)
        qf_teams = []
        r16_pairs = [
            (r16_teams[0], r16_teams[1]),   # R16 L1
            (r16_teams[2], r16_teams[3]),   # R16 L2
            (r16_teams[4], r16_teams[5]),   # R16 L3
            (r16_teams[6], r16_teams[7]),   # R16 L4
            (r16_teams[8], r16_teams[9]),   # R16 R1
            (r16_teams[10], r16_teams[11]), # R16 R2
            (r16_teams[12], r16_teams[13]), # R16 R3
            (r16_teams[14], r16_teams[15]), # R16 R4
        ]

        for home, away in r16_pairs:
            if home in stats: stats[home]["r16"] += 1
            if away in stats: stats[away]["r16"] += 1
            winner = simulate_knockout_match(home, away, all_ratings, avg_goals)
            qf_teams.append(winner)

        # QF — 8 teams → 4 winners
        # Left side QF: L1 winner vs L2 winner, L3 winner vs L4 winner
        # Right side QF: R1 winner vs R2 winner, R3 winner vs R4 winner
        sf_teams = []
        qf_pairs = [
            (qf_teams[0], qf_teams[1]),  # QF L1
            (qf_teams[2], qf_teams[3]),  # QF L2
            (qf_teams[4], qf_teams[5]),  # QF R1
            (qf_teams[6], qf_teams[7]),  # QF R2
        ]

        for home, away in qf_pairs:
            if home in stats: stats[home]["qf"] += 1
            if away in stats: stats[away]["qf"] += 1
            winner = simulate_knockout_match(home, away, all_ratings, avg_goals)
            sf_teams.append(winner)

        # SF — 4 teams → 2 finalists
        # Left SF: QF L1 winner vs QF L2 winner
        # Right SF: QF R1 winner vs QF R2 winner
        final_teams = []
        sf_pairs = [
            (sf_teams[0], sf_teams[1]),  # SF Left
            (sf_teams[2], sf_teams[3]),  # SF Right
        ]

        for home, away in sf_pairs:
            if home in stats: stats[home]["sf"] += 1
            if away in stats: stats[away]["sf"] += 1
            winner = simulate_knockout_match(home, away, all_ratings, avg_goals)
            final_teams.append(winner)

        # Final
        if len(final_teams) == 2:
            for t in final_teams:
                if t in stats: stats[t]["final"] += 1
            champion = simulate_knockout_match(final_teams[0], final_teams[1], all_ratings, avg_goals)
            if champion in stats: stats[champion]["winner"] += 1

    # Convert to percentages
    results = []
    for team, s in stats.items():
        results.append({
            "team": team,
            "win_pct": round(s["winner"] / n_simulations * 100, 2),
            "final_pct": round(s["final"] / n_simulations * 100, 2),
            "semi_pct": round(s["sf"] / n_simulations * 100, 2),
            "quarter_pct": round(s["qf"] / n_simulations * 100, 2),
            "r16_pct": round(s["r16"] / n_simulations * 100, 2),
            "r32_pct": round(s["r32"] / n_simulations * 100, 2),
        })

    results.sort(key=lambda x: -x["win_pct"])
    return results

def run_and_save(n_simulations=10000):
    supabase = get_supabase()

    result = supabase.table("team_ratings")\
        .select("*, team:team_id(name)")\
        .execute()
    all_ratings = {r["team"]["name"]: r for r in result.data if r.get("team")}

    print(f"Loaded ratings for {len(all_ratings)} teams")
    print(f"Running {n_simulations} simulations...")

    results = simulate_tournament(all_ratings, supabase, n_simulations)

    for r in results:
        team_name = r["team"]
        team_result = supabase.table("teams").select("id").eq("name", team_name).execute()
        if not team_result.data:
            continue
        team_id = team_result.data[0]["id"]

        supabase.table("simulation_results").upsert({
            "team_id": team_id,
            "simulations_run": n_simulations,
            "win_pct": r["win_pct"],
            "final_pct": r["final_pct"],
            "semi_pct": r["semi_pct"],
            "quarter_pct": r["quarter_pct"],
            "r16_pct": r["r16_pct"],
            "r32_pct": r["r32_pct"],
            "group_exit_pct": round(100 - r["r32_pct"], 2)
        }, on_conflict="team_id").execute()

    print(f"\nTop 20 World Cup winner probabilities:")
    for i, r in enumerate(results[:20]):
        print(f"{i+1:2}. {r['team']:<25} Win: {r['win_pct']:5.2f}%  Final: {r['final_pct']:5.2f}%  SF: {r['semi_pct']:5.2f}%  QF: {r['quarter_pct']:5.2f}%")

if __name__ == "__main__":
    run_and_save(10000)