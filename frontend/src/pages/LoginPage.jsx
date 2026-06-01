// src/pages/LoginPage.jsx
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { login } from '../services/api'
import useStore from '../store/useStore'
import toast from 'react-hot-toast'

export default function LoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const setAuth = useStore((s) => s.setAuth)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const data = await login(username, password)
      setAuth({ username: data.username, roles: data.roles }, data.access_token)
      toast.success(`Welcome, ${data.username}`)
      navigate('/chat')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <div style={styles.logo}>
          <span style={styles.logoMark}>▲</span>
          <span style={styles.logoText}>VANNA<span style={styles.logoAccent}>.AI</span></span>
        </div>
        <p style={styles.subtitle}>Natural language queries across your databases</p>

        <form onSubmit={handleSubmit} style={styles.form}>
          <label style={styles.label}>Username</label>
          <input
            style={styles.input}
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="hr_admin / it_admin / ..."
            autoComplete="username"
            required
          />

          <label style={styles.label}>Password</label>
          <input
            style={styles.input}
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            autoComplete="current-password"
            required
          />

          <button style={{ ...styles.btn, opacity: loading ? 0.6 : 1 }} disabled={loading}>
            {loading ? 'Signing in…' : 'Sign In →'}
          </button>
        </form>

        <div style={styles.hint}>
          <span style={styles.hintTitle}>Demo credentials:</span>
          {[
            ['hr_admin', 'hr_admin123', 'HR Admin'],
            ['it_admin', 'it_admin123', 'IT Admin'],
            ['hr_viewer', 'hr_viewer123', 'HR Viewer'],
            ['it_viewer', 'it_viewer123', 'IT Viewer'],
          ].map(([u, p, label]) => (
            <button key={u} style={styles.pill} onClick={() => { setUsername(u); setPassword(p) }}>
              {label}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

const styles = {
  page: {
    minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
    background: 'radial-gradient(ellipse at 60% 20%, rgba(99,179,237,0.06) 0%, transparent 60%), var(--bg-0)',
  },
  card: {
    width: 400, background: 'var(--bg-1)', border: '1px solid var(--border)',
    borderRadius: 'var(--radius-lg)', padding: 40, boxShadow: 'var(--shadow)',
  },
  logo: { display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 },
  logoMark: { fontSize: 28, color: 'var(--accent)' },
  logoText: { fontFamily: 'var(--font-mono)', fontSize: 22, fontWeight: 700, letterSpacing: 2 },
  logoAccent: { color: 'var(--accent)' },
  subtitle: { color: 'var(--text-secondary)', marginBottom: 32, fontSize: 13 },
  form: { display: 'flex', flexDirection: 'column', gap: 12 },
  label: { fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: 0.5 },
  input: {
    background: 'var(--bg-2)', border: '1px solid var(--border)', borderRadius: 'var(--radius)',
    padding: '10px 14px', color: 'var(--text-primary)', fontSize: 14, outline: 'none',
    fontFamily: 'var(--font-sans)',
    transition: 'border-color 0.2s',
  },
  btn: {
    marginTop: 8, padding: '12px 20px', background: 'var(--accent)',
    color: '#0a0c10', border: 'none', borderRadius: 'var(--radius)',
    fontWeight: 700, fontSize: 14, fontFamily: 'var(--font-mono)', letterSpacing: 1,
    transition: 'opacity 0.2s',
  },
  hint: { marginTop: 28, paddingTop: 20, borderTop: '1px solid var(--border)' },
  hintTitle: { display: 'block', fontSize: 11, color: 'var(--text-muted)', marginBottom: 10, textTransform: 'uppercase', letterSpacing: 0.5 },
  pill: {
    display: 'inline-block', margin: '3px 4px 3px 0',
    padding: '4px 10px', background: 'var(--bg-3)', border: '1px solid var(--border)',
    borderRadius: 20, fontSize: 12, color: 'var(--text-secondary)', cursor: 'pointer',
    transition: 'border-color 0.2s',
  },
}