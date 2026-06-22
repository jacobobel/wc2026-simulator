import { useState } from 'react'
import { simulateMatch } from '../api'

const TEAMS = [
  'Argentina', 'Australia', 'Austria', 'Belgium', 'Bosnia-Herzegovina',
  'Brazil', 'Canada', 'Cape Verde Islands', 'Colombia', 'Congo DR',
  'Croatia', 'Curaçao', 'Czechia', 'Ecuador', 'Egypt', 'England',
  'France', 'Germany', 'Ghana', 'Haiti', 'Iran', 'Iraq',
  'Ivory Coast', 'Japan', 'Jordan', 'Mexico', 'Morocco', 'Netherlands',
  'New Zealand', 'Norway', 'Panama', 'Paraguay', 'Portugal', 'Qatar',
  'Saudi Arabia', 'Scotland', 'Senegal', 'South Africa', 'South Korea',
  'Spain', 'Sweden', 'Switzerland', 'Tunisia', 'Turkey', 'United States',
  'Uruguay', 'Uzbekistan'
]

export default function Simulator() {
  const [teamA, setTeamA] = useState('Spain')
  const [teamB, setTeamB] = useState('Argentina')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleSimulate = () => {
    setLoading(true)
    simulateMatch(encodeURIComponent(teamA), encodeURIComponent(teamB)).then(res => {
      setResult(res.data)
      setLoading(false)
    })
  }

  return (
    <div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
      <h1 style={{ color: 'white', marginBottom: '0.5rem' }}>Match Simulator</h1>
      <p style={{ color: '#aaa', marginBottom: '2rem' }}>
        Predict any matchup using our Poisson distribution model
      </p>

      <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', marginBottom: '2rem', flexWrap: 'wrap' }}>
        <select
          value={teamA}
          onChange={e => setTeamA(e.target.value)}
          style={{ padding: '0.75rem', borderRadius: '8px', background: '#1a1a2e', color: 'white', border: '1px solid #333', flex: 1 }}
        >
          {TEAMS.map(t => <option key={t} value={t}>{t}</option>)}
        </select>

        <span style={{ color: '#e94560', fontWeight: 'bold', fontSize: '1.2rem' }}>vs</span>

        <select
          value={teamB}
          onChange={e => setTeamB(e.target.value)}
          style={{ padding: '0.75rem', borderRadius: '8px', background: '#1a1a2e', color: 'white', border: '1px solid #333', flex: 1 }}
        >
          {TEAMS.map(t => <option key={t} value={t}>{t}</option>)}
        </select>

        <button
          onClick={handleSimulate}
          disabled={loading}
          style={{
            padding: '0.75rem 1.5rem',
            background: '#e94560',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer',
            fontWeight: 'bold'
          }}
        >
          {loading ? 'Simulating...' : 'Simulate'}
        </button>
      </div>

      {result && (
        <div style={{ background: '#1a1a2e', borderRadius: '12px', padding: '2rem', border: '1px solid #333' }}>
          <h2 style={{ color: 'white', textAlign: 'center', marginBottom: '1.5rem' }}>
            {result.team_a} vs {result.team_b}
          </h2>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ color: '#e94560', fontSize: '2rem', fontWeight: 'bold' }}>
                {(result.prob_a_wins * 100).toFixed(1)}%
              </div>
              <div style={{ color: '#aaa' }}>{result.team_a} Win</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ color: 'white', fontSize: '2rem', fontWeight: 'bold' }}>
                {(result.prob_draw * 100).toFixed(1)}%
              </div>
              <div style={{ color: '#aaa' }}>Draw</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ color: '#e94560', fontSize: '2rem', fontWeight: 'bold' }}>
                {(result.prob_b_wins * 100).toFixed(1)}%
              </div>
              <div style={{ color: '#aaa' }}>{result.team_b} Win</div>
            </div>
          </div>

          <div style={{ textAlign: 'center', borderTop: '1px solid #333', paddingTop: '1rem' }}>
            <div style={{ color: '#aaa', marginBottom: '0.5rem' }}>Most Likely Score</div>
            <div style={{ color: 'white', fontSize: '2rem', fontWeight: 'bold' }}>
              {result.most_likely_score}
            </div>
            <div style={{ color: '#aaa', marginTop: '0.5rem' }}>
              Expected: {result.expected_goals_a} - {result.expected_goals_b}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}