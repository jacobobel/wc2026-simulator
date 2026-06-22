import os
import math
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def get_supabase():
    return create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_KEY")
    )

def poisson_probability(lam, k):
    # P(X=k) = (λ^k × e^-λ) / k!
    return (lam ** k * math.exp(-lam)) / math.factorial(k)

def simulate_match(team_a_ratings, team_b_ratings, max_goals=8):
    # Get global average from database
    supabase = get_supabase()
    config = supabase.table("config").select("value").eq("key", "global_avg_goals").execute()
    avg_goals = config.data[0]["value"] if config.data else 1.5

    attack_a = team_a_ratings["attack_strength"]
    defense_a = team_a_ratings["defense_weakness"]
    attack_b = team_b_ratings["attack_strength"]
    defense_b = team_b_ratings["defense_weakness"]

    # Expected goals for each team
    lambda_a = attack_a * defense_b * avg_goals
    lambda_b = attack_b * defense_a * avg_goals

    # Clamp to reasonable range
    lambda_a = max(0.3, min(lambda_a, 6.0))
    lambda_b = max(0.3, min(lambda_b, 6.0))

    # Build scoreline probability matrix
    score_matrix = {}
    prob_a_wins = 0
    prob_draw = 0
    prob_b_wins = 0

    for i in range(max_goals + 1):
        for j in range(max_goals + 1):
            prob = poisson_probability(lambda_a, i) * poisson_probability(lambda_b, j)
            score_matrix[(i, j)] = prob

            if i > j:
                prob_a_wins += prob
            elif i == j:
                prob_draw += prob
            else:
                prob_b_wins += prob

    # Normalize to account for truncation at max_goals
    total = prob_a_wins + prob_draw + prob_b_wins
    prob_a_wins /= total
    prob_draw /= total
    prob_b_wins /= total

    # Most likely scoreline
    most_likely = max(score_matrix, key=score_matrix.get)

    return {
        "prob_a_wins": round(prob_a_wins, 4),
        "prob_draw": round(prob_draw, 4),
        "prob_b_wins": round(prob_b_wins, 4),
        "expected_goals_a": round(lambda_a, 3),
        "expected_goals_b": round(lambda_b, 3),
        "most_likely_score": f"{most_likely[0]}-{most_likely[1]}",
        "score_matrix": {f"{k[0]}-{k[1]}": round(v, 5) for k, v in score_matrix.items()}
    }

def get_all_ratings(supabase):
    result = supabase.table("team_ratings")\
        .select("*, team:team_id(name)")\
        .execute()
    return {r["team"]["name"]: r for r in result.data if r.get("team")}

def predict_match(team_a_name, team_b_name):
    supabase = get_supabase()
    all_ratings = get_all_ratings(supabase)

    if team_a_name not in all_ratings:
        print(f"Team not found: {team_a_name}")
        return None
    if team_b_name not in all_ratings:
        print(f"Team not found: {team_b_name}")
        return None

    ratings_a = all_ratings[team_a_name]
    ratings_b = all_ratings[team_b_name]

    result = simulate_match(ratings_a, ratings_b)

    print(f"\n{'='*50}")
    print(f"{team_a_name} vs {team_b_name}")
    print(f"{'='*50}")
    print(f"Expected goals: {team_a_name} {result['expected_goals_a']} - {result['expected_goals_b']} {team_b_name}")
    print(f"Most likely score: {result['most_likely_score']}")
    print(f"{team_a_name} win:  {result['prob_a_wins']*100:.1f}%")
    print(f"Draw:              {result['prob_draw']*100:.1f}%")
    print(f"{team_b_name} win:  {result['prob_b_wins']*100:.1f}%")

    return result

if __name__ == "__main__":
    predict_match("Spain", "Morocco")
    predict_match("Argentina", "France")
    predict_match("Spain", "Cape Verde Islands")