# WC2026 Simulator 🏆

A real-time 2026 FIFA World Cup tournament simulator built with statistical modeling and live match data.

**Live Demo**: [wc2026-simulator-ten.vercel.app](https://wc2026-simulator-ten.vercel.app)

## What it does

- Simulates the entire 2026 World Cup **10,000 times** using Monte Carlo simulation
- Calculates win probabilities for all **48 teams** at every tournament stage
- Updates automatically as group stage matches finish
- Predicts any matchup using a **Poisson distribution model**
- Rates teams using a custom **Elo rating system** built from 732+ competitive matches across all 6 confederations

## How it works

### Data Pipeline
- Live match results pulled from **football-data.org API**
- Historical qualifier data (CONMEBOL, UEFA, CAF, CONCACAF, AFC, OFC) parsed from public sources
- Copa America 2024, Euros 2024, AFCON 2025 results included for cross-confederation comparison
- All data stored in **PostgreSQL (Supabase)**

### Rating System
- **Elo ratings** initialized from FIFA rankings, updated after every match
- Weights account for: opponent strength, recency, tournament prestige, goal margin
- World Cup 2026 live matches carry 2x weight vs qualifiers
- Squad quality modifiers for teams where data understates quality (France, Brazil, Portugal)

### Match Simulation
- **Poisson distribution** models expected goals for each team
- λ = attack_strength × opponent_defense_weakness × global_avg_goals
- Full 9×9 scoreline probability matrix computed per match
- Win/draw/loss probabilities derived from matrix

### Tournament Simulation
- Real FIFA 2026 bracket structure (R32 → R16 → QF → SF → Final)
- Correct predetermined group winner vs runner-up matchups
- Best 8 third-place teams selected by points/goal difference
- 10,000 simulations run per update

## Tech Stack

- **Python** — data pipeline, Elo engine, Poisson model, Monte Carlo simulation
- **FastAPI** — REST API backend
- **PostgreSQL / Supabase** — database
- **React + Vite** — frontend
- **Vercel** — frontend deployment
- **Render** — backend deployment

## Project Structure

wc2026-simulator/
├── backend/
│   ├── fetcher/          # API fetchers and data parsers
│   ├── simulation/       # Elo ratings, Poisson model, Monte Carlo
│   ├── api/              # FastAPI endpoints
│   └── pipeline.py       # Full data refresh pipeline
├── frontend/
│   └── src/
│       ├── pages/        # Home, Teams, Simulator
│       └── components/   # Navbar

## Running locally

Backend:
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn backend.api.main:app --reload

Frontend:
cd frontend
npm install
npm run dev

Add a .env file with:
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
FOOTBALL_DATA_API_KEY=your_api_key

## Author

Jacobo Belilty — Computer Engineering student at University of Florida