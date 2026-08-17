// src/components/layout/Sidebar.jsx
import { useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Database, MessageSquare, History, Settings, LogOut, RefreshCw, Sun, Moon, Zap } from 'lucide-react'
import useStore from '../../store/useStore'
import { fetchInstances, logoutUser } from '../../services/api'
import toast from 'react-hot-toast'

export default function Sidebar() {
  const { user, logout, instances, setInstances, activeInstance, setActiveInstance, theme, toggleTheme } = useStore()
  const navigate = useNavigate()
  const location = useLocation()

  useEffect(() => {
    fetchInstances()
      .then(setInstances)
      .catch(() => toast.error('Could not load instances'))
  }, [])

  const handleLogout = async () => {
    try { await logoutUser() } catch (e) {}
    logout()
    navigate('/')
  }

  const grouped = instances.reduce((acc, inst) => {
    if (!acc[inst.group]) acc[inst.group] = []
    acc[inst.group].push(inst)
    return acc
  }, {})

  const isAdmin = user?.roles?.includes('it_admin')

  return (
    <aside style={styles.sidebar}>
      {/* Logo */}
      <div style={styles.brand}>
        <img src="/cppa-logo.png" alt="CPPA Logo" style={{ height: 28, objectFit: 'contain' }} onError={(e) => { e.target.style.display = 'none'; e.target.nextSibling.style.display = 'flex'; }} />
        <Zap size={22} style={{ color: 'var(--accent)', flexShrink: 0, display: 'none' }} className="fallback-logo" />
        <span style={styles.brandText}>CPPA AI Assistant</span>
      </div>

      {/* User pill */}
      <div style={styles.userPill}>
        <span style={styles.avatar}>{user?.username?.[0]?.toUpperCase()}</span>
        <div>
          <div style={styles.userName}>{user?.username}</div>
          <div style={styles.userRoles}>{user?.roles?.join(', ')}</div>
        </div>
      </div>

      <div style={styles.divider} />

      {/* Nav */}
      <nav style={styles.nav}>
        <NavItem icon={<MessageSquare size={15} />} label="Chat" active={location.pathname === '/chat'} onClick={() => navigate('/chat')} />
        <NavItem icon={<History size={15} />} label="Query History" active={location.pathname === '/history'} onClick={() => navigate('/history')} />
        {isAdmin && (
          <NavItem icon={<Settings size={15} />} label="Admin / Training" active={location.pathname === '/admin'} onClick={() => navigate('/admin')} />
        )}
      </nav>

      <div style={styles.divider} />

      {/* DB Instances */}
      <div style={styles.section}>
        <div style={styles.sectionTitle}>
          <Database size={12} /> Databases
        </div>
        {Object.entries(grouped).map(([group, insts]) => (
          <div key={group} style={styles.group}>
            <div style={styles.groupLabel}>{group}</div>
            {insts.map((inst) => (
              <button
                key={inst.key}
                style={{
                  ...styles.instBtn,
                  ...(activeInstance?.key === inst.key ? styles.instBtnActive : {}),
                }}
                onClick={() => { setActiveInstance(inst); navigate('/chat') }}
              >
                <span style={styles.instDot} />
                <span>{inst.label}</span>
              </button>
            ))}
          </div>
        ))}
      </div>

      <div style={{ flex: 1 }} />

      {/* Theme Toggle */}
      <button style={styles.themeToggleBtn} onClick={toggleTheme}>
        {theme === 'dark' ? <Sun size={14} style={{ color: 'var(--warning)' }} /> : <Moon size={14} style={{ color: 'var(--accent)' }} />}
        <span style={{ flex: 1 }}>{theme === 'dark' ? 'Light Mode' : 'Dark Mode'}</span>
        <div style={{
          ...styles.toggleTrack,
          background: theme === 'dark' ? 'var(--bg-3)' : 'var(--accent)',
        }}>
          <div style={{
            ...styles.toggleThumb,
            transform: theme === 'dark' ? 'translateX(0)' : 'translateX(14px)',
          }} />
        </div>
      </button>

      {/* Logout */}
      <button style={styles.logoutBtn} onClick={handleLogout}>
        <LogOut size={14} /> Sign out
      </button>
    </aside>
  )
}

function NavItem({ icon, label, active, onClick }) {
  return (
    <button
      onClick={onClick}
      style={{ ...styles.navItem, ...(active ? styles.navItemActive : {}) }}
    >
      {icon} {label}
    </button>
  )
}

const styles = {
  sidebar: {
    width: 240, minHeight: '100vh', background: 'var(--bg-1)',
    borderRight: '1px solid var(--border)', display: 'flex', flexDirection: 'column',
    padding: '20px 12px', gap: 4,
  },
  brand: { display: 'flex', alignItems: 'center', gap: 8, paddingLeft: 8, marginBottom: 16 },
  brandMark: { fontSize: 20, color: 'var(--accent)' },
  brandText: { fontSize: 15, fontWeight: 700, whiteSpace: 'nowrap' },
  brandAccent: { color: 'var(--accent)' },
  userPill: {
    display: 'flex', alignItems: 'center', gap: 10,
    background: 'var(--bg-2)', borderRadius: 'var(--radius)', padding: '8px 10px',
  },
  avatar: {
    width: 28, height: 28, borderRadius: '50%', background: 'var(--accent)',
    color: '#ffffff', display: 'flex', alignItems: 'center', justifyContent: 'center',
    fontWeight: 700, fontSize: 13,
  },
  userName: { fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' },
  userRoles: { fontSize: 11, color: 'var(--text-muted)' },
  divider: { height: 1, background: 'var(--border)', margin: '12px 0' },
  nav: { display: 'flex', flexDirection: 'column', gap: 2 },
  navItem: {
    display: 'flex', alignItems: 'center', gap: 8, padding: '8px 12px',
    borderRadius: 'var(--radius)', background: 'transparent', border: 'none',
    color: 'var(--text-secondary)', fontSize: 13, fontWeight: 500, textAlign: 'left',
    transition: 'background 0.15s, color 0.15s',
  },
  navItemActive: { background: 'var(--accent-dim)', color: 'var(--accent)' },
  section: { display: 'flex', flexDirection: 'column', gap: 2 },
  sectionTitle: {
    display: 'flex', alignItems: 'center', gap: 6,
    fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase',
    letterSpacing: 0.8, fontWeight: 600, paddingLeft: 4, marginBottom: 6,
  },
  group: { marginBottom: 8 },
  groupLabel: {
    fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase',
    letterSpacing: 0.5, paddingLeft: 8, marginBottom: 4, fontWeight: 700,
  },
  instBtn: {
    display: 'flex', alignItems: 'center', gap: 8, width: '100%',
    padding: '7px 10px', borderRadius: 'var(--radius)',
    background: 'transparent', border: 'none',
    color: 'var(--text-secondary)', fontSize: 12, textAlign: 'left',
    transition: 'background 0.15s, color 0.15s',
  },
  instBtnActive: { background: 'var(--accent-dim)', color: 'var(--accent)' },
  instDot: {
    width: 6, height: 6, borderRadius: '50%',
    background: 'var(--success)', flexShrink: 0,
  },
  themeToggleBtn: {
    display: 'flex', alignItems: 'center', gap: 8, width: '100%',
    padding: '8px 10px', borderRadius: 'var(--radius)',
    background: 'var(--bg-2)', border: '1px solid var(--border)',
    color: 'var(--text-primary)', fontSize: 12, fontWeight: 500, textAlign: 'left',
    marginBottom: 4, transition: 'all 0.2s ease', cursor: 'pointer',
  },
  toggleTrack: {
    width: 32, height: 18, borderRadius: 10, padding: 2,
    display: 'flex', alignItems: 'center', transition: 'background 0.2s',
  },
  toggleThumb: {
    width: 14, height: 14, borderRadius: '50%', background: '#ffffff',
    transition: 'transform 0.2s ease', boxShadow: '0 1px 3px rgba(0,0,0,0.3)',
  },
  logoutBtn: {
    display: 'flex', alignItems: 'center', gap: 8,
    padding: '8px 12px', borderRadius: 'var(--radius)',
    background: 'var(--bg-2)', border: '1px solid var(--border)',
    color: 'var(--text-primary)', fontSize: 13, fontWeight: 600,
    cursor: 'pointer', transition: 'all 0.15s ease',
  },
}