// src/components/layout/Sidebar.jsx
import { useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Database, MessageSquare, Settings, LogOut, RefreshCw } from 'lucide-react'
import useStore from '../../store/useStore'
import { fetchInstances } from '../../services/api'
import toast from 'react-hot-toast'

export default function Sidebar() {
  const { user, logout, instances, setInstances, activeInstance, setActiveInstance } = useStore()
  const navigate = useNavigate()
  const location = useLocation()

  useEffect(() => {
    fetchInstances()
      .then(setInstances)
      .catch(() => toast.error('Could not load instances'))
  }, [])

  const handleLogout = () => { logout(); navigate('/') }

  const grouped = instances.reduce((acc, inst) => {
    if (!acc[inst.group]) acc[inst.group] = []
    acc[inst.group].push(inst)
    return acc
  }, {})

  const isAdmin = user?.roles?.some((r) => r.endsWith('_admin'))

  return (
    <aside style={styles.sidebar}>
      {/* Logo */}
      <div style={styles.brand}>
        <span style={styles.brandMark}>▲</span>
        <span style={styles.brandText}>VANNA<span style={styles.brandAccent}>.AI</span></span>
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
  brandText: { fontFamily: 'var(--font-mono)', fontSize: 16, fontWeight: 700, letterSpacing: 2 },
  brandAccent: { color: 'var(--accent)' },
  userPill: {
    display: 'flex', alignItems: 'center', gap: 10,
    background: 'var(--bg-2)', borderRadius: 'var(--radius)', padding: '8px 10px',
  },
  avatar: {
    width: 28, height: 28, borderRadius: '50%', background: 'var(--accent)',
    color: '#0a0c10', display: 'flex', alignItems: 'center', justifyContent: 'center',
    fontWeight: 700, fontSize: 13,
  },
  userName: { fontSize: 13, fontWeight: 600 },
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
  logoutBtn: {
    display: 'flex', alignItems: 'center', gap: 8,
    padding: '8px 12px', borderRadius: 'var(--radius)',
    background: 'transparent', border: 'none',
    color: 'var(--text-muted)', fontSize: 13,
    transition: 'color 0.15s',
  },
}