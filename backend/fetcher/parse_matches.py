import re
import sys
import os
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.fifa_rankings import FIFA_RANKINGS

TEAM_MAP = {
    "ARG": "Argentina", "BRA": "Brazil", "URU": "Uruguay",
    "COL": "Colombia", "ECU": "Ecuador", "PAR": "Paraguay",
    "CHI": "Chile", "PER": "Peru", "BOL": "Bolivia",
    "VEN": "Venezuela", "ESP": "Spain", "GER": "Germany",
    "FRA": "France", "POR": "Portugal", "ENG": "England",
    "NED": "Netherlands", "BEL": "Belgium", "ITA": "Italy",
    "CRO": "Croatia", "AUT": "Austria", "DEN": "Denmark",
    "SUI": "Switzerland", "SRB": "Serbia", "CZE": "Czechia",
    "HUN": "Hungary", "SVK": "Slovakia", "ALB": "Albania",
    "TUR": "Turkey", "GRE": "Greece", "SCO": "Scotland",
    "UKR": "Ukraine", "MAR": "Morocco", "SEN": "Senegal",
    "EGY": "Egypt", "NGA": "Nigeria", "CMR": "Cameroon",
    "CIV": "Ivory Coast", "MLI": "Mali", "RSA": "South Africa",
    "ALG": "Algeria", "GHA": "Ghana", "USA": "United States",
    "MEX": "Mexico", "CAN": "Canada", "PAN": "Panama",
    "CRC": "Costa Rica", "HON": "Honduras", "JPN": "Japan",
    "KOR": "South Korea", "IRN": "Iran", "AUS": "Australia",
    "KSA": "Saudi Arabia", "NZL": "New Zealand", "TUN": "Tunisia",
    "COD": "DR Congo", "VEN": "Venezuela", "UZB": "Uzbekistan",
    "QAT": "Qatar", "IRQ": "Iraq", "BIH": "Bosnia and Herzegovina",
    "CPV": "Cape Verde", "CUW": "Curaçao", "HAI": "Haiti",
    "JOR": "Jordan", "NOR": "Norway", "SWE": "Sweden",
    "WAL": "Wales", "FIN": "Finland", "SVN": "Slovenia",
    "ISR": "Israel", "MNE": "Montenegro", "ISL": "Iceland",
    "KVX": "Kosovo", "MKD": "North Macedonia", "BLR": "Belarus",
    "BFA": "Burkina Faso", "CGO": "Congo", "ZMB": "Zambia",
    "UGA": "Uganda", "TAN": "Tanzania", "GUI": "Guinea",
    "MOZ": "Mozambique", "LBA": "Libya", "CHN": "China",
    "IND": "India", "THA": "Thailand", "VIE": "Vietnam",
    "IDN": "Indonesia", "PHI": "Philippines", "OMA": "Oman",
    "BHR": "Bahrain", "KUW": "Kuwait", "YEM": "Yemen",
    "LIB": "Lebanon", "PLE": "Palestine", "SLB": "Solomon Islands",
    "VAN": "Vanuatu", "TAH": "Tahiti", "FIJ": "Fiji",
    "PNG": "Papua New Guinea", "ASA": "American Samoa",
    "SUD": "Sudan", "ZIM": "Zimbabwe", "BEN": "Benin",
    "RWA": "Rwanda", "MAD": "Madagascar", "NIG": "Niger",
    "MWI": "Malawi", "ANG": "Angola", "MTN": "Mauritania",
    "EQG": "Equatorial Guinea", "COM": "Comoros", "LBR": "Liberia",
    "SLE": "Sierra Leone", "TOG": "Togo", "BRB": "Barbados",
    "SKN": "St. Kitts and Nevis", "GRN": "Grenada",
    "ATG": "Antigua and Barbuda", "BLZ": "Belize",
    "VIN": "St. Vincent and the Grenadines", "DMA": "Dominica",
    "MSR": "Montserrat", "SLV": "El Salvador", "GUA": "Guatemala",
    "TRI": "Trinidad and Tobago", "JAM": "Jamaica",
    "NCA": "Nicaragua", "CUB": "Cuba", "SUR": "Suriname",
    "GUY": "Guyana", "KGZ": "Kyrgyzstan", "TJK": "Tajikistan",
    "KAZ": "Kazakhstan", "ARM": "Armenia", "AZE": "Azerbaijan",
    "GAB": "Gabon", "NAM": "Namibia", "KEN": "Kenya",
    "ETH": "Ethiopia", "ROM": "Romania", "CZE": "Czechia",
}

def parse_team_code(raw):
    match = re.search(r'\|([A-Z]{2,3})\}\}', raw)
    if match:
        code = match.group(1)
        return TEAM_MAP.get(code, code)
    return None

def parse_score(score_str):
    score_str = score_str.strip()
    score_str = score_str.replace('–', '-').replace('−', '-')
    parts = score_str.split('-')
    if len(parts) == 2:
        try:
            return int(parts[0].strip()), int(parts[1].strip())
        except:
            return None, None
    return None, None

def parse_date(date_str):
    match = re.search(r'(\d{4})\|(\d{1,2})\|(\d{1,2})', date_str)
    if match:
        year, month, day = match.groups()
        return datetime(int(year), int(month), int(day)).date()
    return None

def parse_wikipedia_markup(markup, confederation, tournament="World Cup Qualifier"):
    matches = []
    current_matchday = None

    sections = re.split(r'===Matchday (\d+)===', markup)

    i = 1
    while i < len(sections):
        if sections[i].isdigit():
            current_matchday = int(sections[i])
            i += 1
            section_content = sections[i] if i < len(sections) else ""
        else:
            section_content = sections[i]

        boxes = re.split(r'\{\{Football box', section_content)

        for box in boxes[1:]:
            lines = {}
            for line in box.split('\n'):
                if '=' in line and line.strip().startswith('|'):
                    key_val = line.strip()[1:].split('=', 1)
                    if len(key_val) == 2:
                        key = key_val[0].strip()
                        val = key_val[1].strip()
                        lines[key] = val

            team1_raw = lines.get('team1', '')
            team2_raw = lines.get('team2', '')
            score_raw = lines.get('score', '')
            date_raw  = lines.get('date', '')
            stadium_raw = lines.get('stadium', '')

            home_team = parse_team_code(team1_raw)
            away_team = parse_team_code(team2_raw)
            home_score, away_score = parse_score(score_raw)
            match_date = parse_date(date_raw)

            stadium = re.sub(r'\[\[([^\|]+)\|([^\]]+)\]\]', r'\2', stadium_raw)
            stadium = re.sub(r'\[\[([^\]]+)\]\]', r'\1', stadium)

            if all([home_team, away_team, home_score is not None,
                    away_score is not None, match_date]):
                matches.append({
                    "home_team": home_team,
                    "away_team": away_team,
                    "home_score": home_score,
                    "away_score": away_score,
                    "match_date": str(match_date),
                    "confederation": confederation,
                    "tournament": tournament,
                    "tournament_stage": "Qualifier",
                    "matchday": current_matchday,
                    "stadium": stadium[:200] if stadium else None,
                    "home_team_fifa_ranking": FIFA_RANKINGS.get(home_team),
                    "away_team_fifa_ranking": FIFA_RANKINGS.get(away_team)
                })

        i += 1

    return matches
load_dotenv()

def get_supabase():
    return create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_KEY")
    )

def save_matches_to_db(matches):
    supabase = get_supabase()
    inserted = 0
    skipped = 0

    for match in matches:
        try:
            supabase.table("competitive_matches").upsert(
                match,
                on_conflict="home_team,away_team,match_date"
            ).execute()
            inserted += 1
        except Exception as e:
            print(f"Error inserting {match['home_team']} vs {match['away_team']}: {e}")
            skipped += 1

    print(f"Saved {inserted} matches, skipped {skipped}")


if __name__ == "__main__":
    # Read CONMEBOL qualifier data from file
    with open("backend/data/conmebol_qualifiers.txt", "r", encoding="utf-8") as f:
        markup = f.read()
    
    results = parse_wikipedia_markup(markup, "CONMEBOL")
    print(f"Parsed {len(results)} matches")
    
    print("\nSaving to database...")
    save_matches_to_db(results)