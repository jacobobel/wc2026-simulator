import os
import math
from datetime import datetime, date
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def get_supabase():
    return create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_KEY")
    )

def fifa_ranking_to_elo(ranking):
    if not ranking:
        return 1500
    return max(1000, 2000 - (ranking - 1) * 12)

def expected_result(rating_a, rating_b):
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

def get_tournament_weight(tournament, stage):
    tournament = (tournament or "").lower()
    stage = (stage or "").lower()

    if "final" == stage.strip():
        stage_mult = 2.0
    elif "semi" in stage:
        stage_mult = 1.8
    elif "quarter" in stage:
        stage_mult = 1.6
    elif "round of" in stage or "r16" in stage or "last 16" in stage:
        stage_mult = 1.4
    elif "knockout" in stage or "playoff" in stage:
        stage_mult = 1.3
    else:
        stage_mult = 1.0

    if "world cup 2026" in tournament:
        tournament_mult = 2.0
    elif "world cup" in tournament and "qualifier" not in tournament:
        tournament_mult = 1.8
    elif any(t in tournament for t in ["copa america", "euros", "euro 2024", "afcon"]):
        tournament_mult = 1.6
    elif "qualifier" in tournament:
        tournament_mult = 1.0
    else:
        tournament_mult = 1.2

    return stage_mult * tournament_mult

def get_recency_weight(match_date_str, reference_date=None):
    if not reference_date:
        reference_date = date.today()
    try:
        if isinstance(match_date_str, str):
            match_date = datetime.strptime(match_date_str[:10], "%Y-%m-%d").date()
        else:
            match_date = match_date_str
        days_ago = (reference_date - match_date).days
        return math.exp(-0.0003 * days_ago)
    except:
        return 1.0

def get_margin_weight(goal_diff):
    return math.log(abs(goal_diff) + 1) + 1

def calculate_ratings():
    supabase = get_supabase()

    result = supabase.table("competitive_matches")\
        .select("*")\
        .order("match_date")\
        .execute()
    matches = result.data
    print(f"Loaded {len(matches)} competitive matches")

    wc_result = supabase.table("matches")\
        .select("*, home:home_team_id(name), away:away_team_id(name)")\
        .eq("status", "FINISHED")\
        .order("match_date")\
        .execute()
    wc_matches = wc_result.data
    print(f"Loaded {len(wc_matches)} completed WC 2026 matches")

    for m in wc_matches:
        if m.get("home") and m.get("away"):
            matches.append({
                "home_team": m["home"]["name"],
                "away_team": m["away"]["name"],
                "home_score": m["home_score"],
                "away_score": m["away_score"],
                "match_date": m["match_date"],
                "tournament": "World Cup 2026",
                "tournament_stage": m["stage"],
                "home_team_fifa_ranking": None,
                "away_team_fifa_ranking": None
            })

    matches.sort(key=lambda x: x.get("match_date", ""))
    print(f"Total matches for Elo calculation: {len(matches)}")

    teams_result = supabase.table("teams").select("*").execute()
    teams = teams_result.data

    elo_ratings = {}
    team_ids = {}
    team_data = {}

    HOST_NATIONS = {"United States": 17, "Mexico": 14, "Canada": 30}

    for team in teams:
        name = team["name"]
        fifa_rank = team.get("fifa_ranking")
        starting_elo = fifa_ranking_to_elo(fifa_rank)

        if name in HOST_NATIONS:
            virtual_elo = fifa_ranking_to_elo(HOST_NATIONS[name])
            starting_elo = (starting_elo * 3 + virtual_elo * 2) / 5

        elo_ratings[name] = starting_elo
        team_ids[name] = team["id"]
        team_data[name] = {
            "fifa_ranking": fifa_rank,
            "goals_scored_weighted": 0,
            "goals_conceded_weighted": 0,
            "total_weight": 0,
            "matches_played": 0
        }

    print(f"Initialized {len(elo_ratings)} teams")
    print(f"Argentina starting Elo: {elo_ratings.get('Argentina', 'N/A')}")
    print(f"New Zealand starting Elo: {elo_ratings.get('New Zealand', 'N/A')}")

    for match in matches:
        home = match["home_team"]
        away = match["away_team"]
        home_score = match["home_score"]
        away_score = match["away_score"]
        tournament = match.get("tournament", "")
        stage = match.get("tournament_stage", "")
        match_date = match.get("match_date", "")
        home_ranking = match.get("home_team_fifa_ranking") or 100
        away_ranking = match.get("away_team_fifa_ranking") or 100

        home_in_wc = home in elo_ratings
        away_in_wc = away in elo_ratings

        tournament_weight = get_tournament_weight(tournament, stage)
        recency_weight = get_recency_weight(match_date)
        goal_diff = abs(home_score - away_score)
        margin_weight = get_margin_weight(goal_diff)

        K = 32 * tournament_weight * recency_weight * margin_weight

        if home_score > away_score:
            home_actual = 1.0
            away_actual = 0.0
        elif home_score < away_score:
            home_actual = 0.0
            away_actual = 1.0
        else:
            home_actual = 0.5
            away_actual = 0.5

        if home_in_wc and away_in_wc:
            home_expected = expected_result(elo_ratings[home], elo_ratings[away])
            away_expected = expected_result(elo_ratings[away], elo_ratings[home])
            elo_ratings[home] += K * (home_actual - home_expected)
            elo_ratings[away] += K * (away_actual - away_expected)

        elif home_in_wc:
            proxy_elo = fifa_ranking_to_elo(away_ranking)
            home_expected = expected_result(elo_ratings[home], proxy_elo)
            elo_ratings[home] += K * (home_actual - home_expected)

        elif away_in_wc:
            proxy_elo = fifa_ranking_to_elo(home_ranking)
            away_expected = expected_result(elo_ratings[away], proxy_elo)
            elo_ratings[away] += K * (away_actual - away_expected)

        if home_in_wc:
            w = 1 / math.log(away_ranking + 1) * recency_weight
            team_data[home]["goals_scored_weighted"] += home_score * w
            team_data[home]["goals_conceded_weighted"] += away_score * w
            team_data[home]["total_weight"] += w
            team_data[home]["matches_played"] += 1

        if away_in_wc:
            w = 1 / math.log(home_ranking + 1) * recency_weight
            team_data[away]["goals_scored_weighted"] += away_score * w
            team_data[away]["goals_conceded_weighted"] += home_score * w
            team_data[away]["total_weight"] += w
            team_data[away]["matches_played"] += 1

    global_scored = sum(d["goals_scored_weighted"] for d in team_data.values())
    global_weight = sum(d["total_weight"] for d in team_data.values())
    global_avg = global_scored / global_weight if global_weight > 0 else 1.5

    supabase.table("config").upsert(
        {"key": "global_avg_goals", "value": global_avg},
        on_conflict="key"
    ).execute()
    print(f"Global average goals saved: {global_avg:.4f}")

    min_elo = min(elo_ratings.values())
    max_elo = max(elo_ratings.values())
    elo_range = max_elo - min_elo

    ratings = []
    for name in elo_ratings:
        elo = elo_ratings[name]
        data = team_data[name]

        compressed_elo = 1500 + (elo - 1500) * 0.4
        composite = 0.5 + (compressed_elo - min_elo) / (max_elo - min_elo) * 1.5 if elo_range > 0 else 1.0

        elo_normalized = (compressed_elo - 1400) / 600
        elo_normalized = max(0.1, min(elo_normalized, 1.2))

        attack_strength = 0.6 + elo_normalized * 1.0
        defense_weakness = 1.4 - elo_normalized * 0.9

        if data["total_weight"] > 0:
            avg_scored = data["goals_scored_weighted"] / data["total_weight"]
            avg_conceded = data["goals_conceded_weighted"] / data["total_weight"]
            raw_attack = avg_scored / global_avg
            raw_defense = avg_conceded / global_avg

            matches_played = data["matches_played"]
            data_trust = min(matches_played / 50, 0.3)

            raw_attack = max(0.7, min(raw_attack, 2.0))
            raw_defense = max(0.5, min(raw_defense, 1.8))

            attack_strength = (data_trust * raw_attack) + ((1 - data_trust) * attack_strength)
            defense_weakness = (data_trust * raw_defense) + ((1 - data_trust) * defense_weakness)

            avg_scored = attack_strength * global_avg
            avg_conceded = defense_weakness * global_avg
        else:
            avg_scored = attack_strength * global_avg
            avg_conceded = defense_weakness * global_avg

        # Apply squad modifier if exists
        modifier_result = supabase.table("squad_modifiers")\
            .select("*")\
            .eq("team_name", name)\
            .execute()

        if modifier_result.data:
            mod = modifier_result.data[0]
            attack_strength *= mod["attack_boost"]
            defense_weakness /= mod["defense_boost"]  # divide because lower is better

        form_score = attack_strength / (defense_weakness + 0.1)

        rating_data = {
            "team_id": team_ids[name],
            "attack_strength": round(attack_strength, 4),
            "defense_weakness": round(defense_weakness, 4),
            "form_score": round(form_score, 4),
            "avg_goals_scored": round(avg_scored, 4),
            "avg_goals_conceded": round(avg_conceded, 4),
            "composite_rating": round(composite, 4),
            "schedule_difficulty": round(elo, 2)
        }

        ratings.append((name, rating_data, elo))

    for name, rating_data, elo in ratings:
        supabase.table("team_ratings").upsert(
            rating_data,
            on_conflict="team_id"
        ).execute()

    print(f"\nElo ratings calculated and saved for {len(ratings)} teams")
    print("\nTop 20 by Elo rating:")
    sorted_ratings = sorted(ratings, key=lambda x: x[2], reverse=True)
    for i, (name, r, elo) in enumerate(sorted_ratings[:20]):
        print(f"{i+1:2}. {name:<25} Elo={elo:7.1f}  attack={r['attack_strength']}  defense={r['defense_weakness']}  composite={r['composite_rating']}")

if __name__ == "__main__":
    calculate_ratings()