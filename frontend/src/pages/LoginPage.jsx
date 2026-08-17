// src/pages/LoginPage.jsx
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Eye, EyeOff, Zap } from 'lucide-react'
import { login, loginWindows } from '../services/api'
import useStore from '../store/useStore'
import toast from 'react-hot-toast'

export default function LoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showStandardPassword, setShowStandardPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const setAuth = useStore((s) => s.setAuth)
  const navigate = useNavigate()

  // Windows Authentication Popup State
  const [showWindowsPopup, setShowWindowsPopup] = useState(true)
  const [winUsername, setWinUsername] = useState('')
  const [winPassword, setWinPassword] = useState('')
  const [showWinPassword, setShowWinPassword] = useState(false)
  const [winDomain, setWinDomain] = useState('CPPA')
  const [winLoading, setWinLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const data = await login(username, password)
      const target = localStorage.getItem('redirectAfterLogin') || '/chat'
      if (target.startsWith('/share/')) {
        const sid = target.split('/share/')[1]
        if (sid) sessionStorage.setItem(`share_authed_${sid}`, 'true')
      }
      localStorage.removeItem('redirectAfterLogin')
      navigate(target)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  const handleWindowsSubmit = async (e) => {
    e.preventDefault()
    setWinLoading(true)
    try {
      const data = await loginWindows(winUsername, winPassword, winDomain)
      setAuth({ username: data.username, roles: data.roles }, data.access_token)
      toast.success(`Windows login successful! Welcome, ${data.username}`)
      const target = localStorage.getItem('redirectAfterLogin') || '/chat'
      if (target.startsWith('/share/')) {
        const sid = target.split('/share/')[1]
        if (sid) sessionStorage.setItem(`share_authed_${sid}`, 'true')
      }
      localStorage.removeItem('redirectAfterLogin')
      navigate(target)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Windows Authentication failed')
    } finally {
      setWinLoading(false)
    }
  }

  const handleCancelWindows = () => {
    setShowWindowsPopup(false)
    toast.success('Windows authentication bypassed. Standard login enabled.')
  }

  return (
    <div style={styles.page}>
      {/* Windows Security Popup Modal */}
      {showWindowsPopup && (
        <div style={styles.modalOverlay}>
          <div style={styles.modalCard}>
            <div style={styles.modalHeader}>
              <div style={styles.modalHeaderTitle}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="#3b82f6" style={{ marginRight: 6 }}>
                  <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-5.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8Secondaryz" />
                </svg>
                Windows Security
              </div>
              <button style={styles.modalCloseBtn} onClick={handleCancelWindows}>×</button>
            </div>
            <div style={styles.modalBody}>
              <div style={styles.modalBranding}>
                <div>
                  <h2 style={styles.modalTitle}>Sign in to access this site</h2>
                  <p style={styles.modalSubtitle}>Authorization required for CPPA AI Assistant</p>
                </div>
              </div>
              
              <form onSubmit={handleWindowsSubmit} style={styles.modalForm}>
                <div style={styles.inputGroup}>
                  <label style={styles.modalLabel}>User name</label>
                  <input
                    style={styles.modalInput}
                    value={winUsername}
                    onChange={(e) => setWinUsername(e.target.value)}
                    placeholder="e.g. amna.malik"
                    required
                    autoFocus
                  />
                </div>
                
                <div style={styles.inputGroup}>
                  <label style={styles.modalLabel}>Password</label>
                  <div style={{ position: 'relative' }}>
                    <input
                      style={{ ...styles.modalInput, paddingRight: 36 }}
                      type={showWinPassword ? 'text' : 'password'}
                      value={winPassword}
                      onChange={(e) => setWinPassword(e.target.value)}
                      placeholder="••••••••••••"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowWinPassword(!showWinPassword)}
                      style={styles.eyeBtn}
                      tabIndex={-1}
                      title={showWinPassword ? 'Hide Password' : 'Show Password'}
                    >
                      {showWinPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>
                </div>

                <div style={styles.inputGroup}>
                  <label style={styles.modalLabel}>Domain</label>
                  <input
                    style={styles.modalInput}
                    value={winDomain}
                    onChange={(e) => setWinDomain(e.target.value)}
                    placeholder="CPPA"
                  />
                </div>
                
                <div style={styles.modalActions}>
                  <button type="submit" style={styles.okBtn} disabled={winLoading}>
                    {winLoading ? 'Logging in...' : 'OK'}
                  </button>
                  <button type="button" style={styles.cancelBtn} onClick={handleCancelWindows} disabled={winLoading}>
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Background/Standard Login Page Card */}
      <div style={{ ...styles.card, opacity: showWindowsPopup ? 0.3 : 1, transition: 'opacity 0.3s' }}>
        <div style={styles.logo}>
          <img src="/cppa-logo.png" alt="CPPA Logo" style={{ height: 42, objectFit: 'contain' }} onError={(e) => { e.target.style.display = 'none'; e.target.nextSibling.style.display = 'flex'; }} />
          <Zap size={32} style={{ color: 'var(--accent)', flexShrink: 0, display: 'none' }} className="fallback-logo" />
          <span style={styles.logoText}>CPPA AI Assistant</span>
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
            disabled={showWindowsPopup}
          />

          <label style={styles.label}>Password</label>
          <div style={{ position: 'relative' }}>
            <input
              style={{ ...styles.input, paddingRight: 36 }}
              type={showStandardPassword ? 'text' : 'password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              autoComplete="current-password"
              required
              disabled={showWindowsPopup}
            />
            <button
              type="button"
              onClick={() => setShowStandardPassword(!showStandardPassword)}
              style={styles.eyeBtn}
              tabIndex={-1}
              disabled={showWindowsPopup}
              title={showStandardPassword ? 'Hide Password' : 'Show Password'}
            >
              {showStandardPassword ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>

          <button 
            style={{ ...styles.btn, opacity: (loading || showWindowsPopup) ? 0.6 : 1 }} 
            disabled={loading || showWindowsPopup}
          >
            {loading ? 'Signing in…' : 'Sign In →'}
          </button>
        </form>

        <div style={styles.hint}>
          <div style={styles.hintHeader}>
            <span style={styles.hintTitle}>Demo credentials:</span>
            <button 
              style={styles.windowsBtn}
              onClick={() => setShowWindowsPopup(true)}
            >
              🔒 Windows Logon
            </button>
          </div>
          {[
            ['hr_admin', 'hr_admin123', 'HR Admin'],
            ['it_admin', 'it_admin123', 'IT Admin'],
            ['hr_viewer', 'hr_viewer123', 'HR Viewer'],
            ['it_viewer', 'it_viewer123', 'IT Viewer'],
          ].map(([u, p, label]) => (
            <button 
              key={u} 
              style={styles.pill} 
              onClick={() => { setUsername(u); setPassword(p) }}
              disabled={showWindowsPopup}
            >
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
    position: 'relative',
  },
  card: {
    width: 400, background: 'var(--bg-1)', border: '1px solid var(--border)',
    borderRadius: 'var(--radius-lg)', padding: 40, boxShadow: 'var(--shadow)',
  },
  logo: { display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 },
  logoMark: { fontSize: 28, color: 'var(--accent)' },
  logoText: { fontSize: 22, fontWeight: 700 },
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
  hintHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 },
  hintTitle: { fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 0.5 },
  windowsBtn: {
    background: 'rgba(59,130,246,0.1)', border: '1px solid rgba(59,130,246,0.4)',
    borderRadius: 12, padding: '4px 10px', color: '#60a5fa', fontSize: 11,
    fontWeight: 600, cursor: 'pointer', transition: 'all 0.2s',
  },
  pill: {
    display: 'inline-block', margin: '3px 4px 3px 0',
    padding: '4px 10px', background: 'var(--bg-3)', border: '1px solid var(--border)',
    borderRadius: 20, fontSize: 12, color: 'var(--text-secondary)', cursor: 'pointer',
    transition: 'border-color 0.2s',
  },

  // Modal styling (Realistic Windows Security modal theme)
  modalOverlay: {
    position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.7)', display: 'flex',
    alignItems: 'center', justifyContent: 'center', zIndex: 1000,
    backdropFilter: 'blur(3px)',
  },
  modalCard: {
    width: 420, background: '#202634', border: '1px solid #3b82f6',
    borderRadius: 6, boxShadow: '0 25px 50px -12px rgba(0,0,0,0.6)',
    overflow: 'hidden', fontFamily: '"Segoe UI", system-ui, sans-serif',
  },
  modalHeader: {
    background: '#171c26', padding: '10px 16px', borderBottom: '1px solid #2e374a',
    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
  },
  modalHeaderTitle: {
    fontSize: 13, fontWeight: 600, color: '#94a3b8', display: 'flex', alignItems: 'center', gap: 6,
  },
  shieldIcon: { fontSize: 14, color: '#3b82f6' },
  modalCloseBtn: {
    background: 'none', border: 'none', color: '#94a3b8', fontSize: 18,
    cursor: 'pointer', padding: '0 4px', lineHeight: 1,
  },
  modalBody: { padding: '24px 28px' },
  modalBranding: { display: 'flex', gap: 14, marginBottom: 22, alignItems: 'center' },
  modalLockIcon: { fontSize: 28 },
  modalTitle: { fontSize: 18, fontWeight: 500, color: '#ffffff', margin: 0 },
  modalSubtitle: { fontSize: 12, color: '#94a3b8', margin: '4px 0 0 0' },
  modalForm: { display: 'flex', flexDirection: 'column', gap: 14 },
  inputGroup: { display: 'flex', flexDirection: 'column', gap: 4 },
  modalLabel: { fontSize: 11, fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: 0.5 },
  modalInput: {
    background: '#0f131a', border: '1px solid #334155', borderRadius: 4,
    padding: '8px 12px', color: '#ffffff', fontSize: 13, outline: 'none',
    transition: 'border-color 0.2s', width: '100%', boxSizing: 'border-box',
  },
  eyeBtn: {
    position: 'absolute', right: 10, top: '50%', transform: 'translateY(-50%)',
    background: 'transparent', border: 'none', color: '#94a3b8',
    cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center',
    padding: 2, zIndex: 5,
  },
  modalActions: { display: 'flex', justifyContent: 'flex-end', gap: 10, marginTop: 12 },
  okBtn: {
    padding: '6px 20px', background: '#2563eb', color: '#ffffff', border: 'none', borderRadius: 4,
    fontWeight: 600, fontSize: 12, cursor: 'pointer', minWidth: 70, textAlign: 'center',
    transition: 'background-color 0.2s',
  },
  cancelBtn: {
    padding: '6px 20px', background: 'transparent', color: '#94a3b8', border: '1px solid #475569', borderRadius: 4,
    fontWeight: 600, fontSize: 12, cursor: 'pointer', minWidth: 70, textAlign: 'center',
    transition: 'background-color 0.2s, color 0.2s',
  },
}