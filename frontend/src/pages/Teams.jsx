import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getGroups } from '../api'

export default function Teams() {
  const [groups, setGroups] = useState({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getGroups().then(res => {
      setGroups(res.data)
      setLoading(false)
    })
  }, [])

  if (loading) return (
    <div style={{ color: 'white', textAlign: 'center', padding: '4rem' }}>
      Loading groups...
    </div>
  )

  return (
    <div style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      <h1 style={{ color: 'white', marginBottom: '2rem' }}>All 48 Teams by Group</h1>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1.5rem' }}>
        {Object.entries(groups).sort().map(([group, teams]) => (
          <div key={group} style={{
            background: '#1a1a2e',
            borderRadius: '8px',
            padding: '1.5rem',
            border: '1px solid #333'
          }}>
            <h2 style={{ color: '#e94560', marginBottom: '1rem' }}>Group {group}</h2>
            {teams.map(team => (
              <Link
                key={team.name}
                to={`/teams/${encodeURIComponent(team.name)}`}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.75rem',
                  padding: '0.5rem 0',
                  color: 'white',
                  textDecoration: 'none',
                  borderBottom: '1px solid #222'
                }}
              >
                {team.crest_url && (
                  <img
                    src={team.crest_url}
                    alt={team.name}
                    style={{ width: '28px', height: '28px', objectFit: 'contain' }}
                  />
                )}
                <span>{team.name}</span>
                {team.simulation_results?.[0] && (
                  <span style={{ marginLeft: 'auto', color: '#e94560', fontSize: '0.85rem' }}>
                    {team.simulation_results[0].win_pct}%
                  </span>
                )}
              </Link>
            ))}
          </div>
        ))}
      </div>
    </div>
  )
}