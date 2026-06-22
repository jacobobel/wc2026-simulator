import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getOdds } from '../api'

export default function Home() {
  const [odds, setOdds] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getOdds().then(res => {
      setOdds(res.data)
      setLoading(false)
    })
  }, [])

  if (loading) return (
    <div style={{ color: 'white', textAlign: 'center', padding: '4rem' }}>
      Loading simulations...
    </div>
  )

  return (
    <div style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      <h1 style={{ color: 'white', marginBottom: '0.5rem' }}>
        2026 World Cup Simulator
      </h1>
      <p style={{ color: '#aaa', marginBottom: '2rem' }}>
        Based on 10,000 Monte Carlo simulations using Elo ratings, 
        Poisson modeling, and live match data
      </p>

      <h2 style={{ color: '#e94560', marginBottom: '1rem' }}>
        🏆 Championship Odds
      </h2>

      <div style={{ overflowX: 'auto' }}>
        <table style={{ 
          width: '100%', 
          borderCollapse: 'collapse',
          color: 'white'
        }}>
          <thead>
            <tr style={{ borderBottom: '2px solid #e94560' }}>
              <th style={{ padding: '0.75rem', textAlign: 'left' }}>Rank</th>
              <th style={{ padding: '0.75rem', textAlign: 'left' }}>Team</th>
              <th style={{ padding: '0.75rem', textAlign: 'center' }}>Win</th>
              <th style={{ padding: '0.75rem', textAlign: 'center' }}>Final</th>
              <th style={{ padding: '0.75rem', textAlign: 'center' }}>Semi</th>
              <th style={{ padding: '0.75rem', textAlign: 'center' }}>Quarter</th>
              <th style={{ padding: '0.75rem', textAlign: 'center' }}>R16</th>
              <th style={{ padding: '0.75rem', textAlign: 'center' }}>Advance</th>
            </tr>
          </thead>
          <tbody>
            {odds.map((team, index) => (
              <tr key={team.id} style={{ 
                borderBottom: '1px solid #333',
                background: index % 2 === 0 ? '#1a1a2e' : '#16213e'
              }}>
                <td style={{ padding: '0.75rem', color: '#aaa' }}>{index + 1}</td>
                <td style={{ padding: '0.75rem' }}>
                  <Link 
                    to={`/teams/${encodeURIComponent(team.team.name)}`}
                    style={{ 
                      color: 'white', 
                      textDecoration: 'none',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem'
                    }}
                  >
                    {team.team.crest_url && (
                      <img 
                        src={team.team.crest_url} 
                        alt={team.team.name}
                        style={{ width: '24px', height: '24px', objectFit: 'contain' }}
                      />
                    )}
                    {team.team.name}
                  </Link>
                </td>
                <td style={{ padding: '0.75rem', textAlign: 'center', color: '#e94560', fontWeight: 'bold' }}>
                  {team.win_pct}%
                </td>
                <td style={{ padding: '0.75rem', textAlign: 'center' }}>{team.final_pct}%</td>
                <td style={{ padding: '0.75rem', textAlign: 'center' }}>{team.semi_pct}%</td>
                <td style={{ padding: '0.75rem', textAlign: 'center' }}>{team.quarter_pct}%</td>
                <td style={{ padding: '0.75rem', textAlign: 'center' }}>{team.r16_pct}%</td>
                <td style={{ padding: '0.75rem', textAlign: 'center' }}>
                  <div style={{
                    background: '#e94560',
                    borderRadius: '4px',
                    height: '8px',
                    width: `${team.r32_pct}%`,
                    minWidth: '4px'
                  }} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}