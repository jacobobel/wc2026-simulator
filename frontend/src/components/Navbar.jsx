import { Link } from 'react-router-dom'

export default function Navbar() {
  return (
    <nav style={{
      background: '#1a1a2e',
      padding: '1rem 2rem',
      display: 'flex',
      alignItems: 'center',
      gap: '2rem',
      borderBottom: '2px solid #e94560'
    }}>
      <span style={{ color: '#e94560', fontWeight: 'bold', fontSize: '1.2rem' }}>
        ⚽ WC2026 Simulator
      </span>
      <Link to="/" style={{ color: 'white', textDecoration: 'none' }}>Home</Link>
      <Link to="/teams" style={{ color: 'white', textDecoration: 'none' }}>Teams</Link>
      <Link to="/simulator" style={{ color: 'white', textDecoration: 'none' }}>Match Simulator</Link>
    </nav>
  )
}