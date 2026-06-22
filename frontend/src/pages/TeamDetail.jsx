import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { getTeam } from '../api'

export default function TeamDetail() {
  const { teamName } = useParams()
  const [team, setTeam] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getTeam(decodeURIComponent(teamName)).then(res => {
      setTeam(res.data)
      setLoading(false)
    })
  }, [teamName])

  if (loading) return (
    <div style={{ color: 'white', textAlign: 'center', padding: '4rem' }}>Loading...</div>
  )
  if (!team) return (
    <div style={{ color: 'white', textAlign: 'center', padding: '4rem' }}>Team not found</div>
  )

  const sim = team.simulation_results?.[0]
  const ratings = team.team_ratings?.[0]

  return (
    <div style={{ padding: '2rem', maxWidth: '900px', margin: '0 auto' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', marginBottom: '2rem' }}>
        {team.crest_url && (
          <img src={team.crest_url} alt={team.name} style={{ width: '80px', height: '80px', objectFit: 'contain' }} />
        )}
        <div>
          <h1 style={{ color: 'white', fontSize: '2rem' }}>{team.name}</h1>
          <p style={{ color: '#aaa' }}>Group {team.group_name} · {team.confederation}</p>
        </div>
      </div>

      {sim && (
        <div style={{ marginBottom: '2rem' }}>
          <h2 style={{ color: '#e94560', marginBottom: '1rem' }}>Tournament Odds</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
            {[
              { label: 'Win World Cup', value: sim.win_pct },
              { label: 'Reach Final', value: sim.final_pct },
              { label: 'Reach Semi', value: sim.semi_pct },
              { label: 'Reach Quarter', value: sim.quarter_pct },
              { label: 'Reach R16', value: sim.r16_pct },
              { label: 'Advance R32', value: sim.r32_pct },
            ].map(({ label, value }) => (
              <div key={label} style={{
                background: '#1a1a2e',
                borderRadius: '8px',
                padding: '1rem',
                textAlign: 'center',
                border: '1px solid #333'
              }}>
                <div style={{ color: '#e94560', fontSize: '1.5rem', fontWeight: 'bold' }}>{value}%</div>
                <div style={{ color: '#aaa', fontSize: '0.85rem', marginTop: '0.25rem' }}>{label}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {ratings && (
        <div>
          <h2 style={{ color: '#e94560', marginBottom: '1rem' }}>Team Ratings</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
            {[
              { label: 'Attack Strength', value: ratings.attack_strength },
              { label: 'Defense Weakness', value: ratings.defense_weakness },
              { label: 'Form Score', value: ratings.form_score },
              { label: 'Avg Goals Scored', value: ratings.avg_goals_scored },
              { label: 'Avg Goals Conceded', value: ratings.avg_goals_conceded },
              { label: 'Elo Rating', value: ratings.schedule_difficulty },
            ].map(({ label, value }) => (
              <div key={label} style={{
                background: '#1a1a2e',
                borderRadius: '8px',
                padding: '1rem',
                textAlign: 'center',
                border: '1px solid #333'
              }}>
                <div style={{ color: 'white', fontSize: '1.3rem', fontWeight: 'bold' }}>{value}</div>
                <div style={{ color: '#aaa', fontSize: '0.85rem', marginTop: '0.25rem' }}>{label}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}