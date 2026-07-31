// src/App.jsx
import { useEffect, useState } from 'react'
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import useStore from './store/useStore'
import LoginPage from './pages/LoginPage'
import ChatPage from './pages/ChatPage'
import AdminPage from './pages/AdminPage'
import HistoryPage from './pages/HistoryPage'
import ShareChatPage from './pages/ShareChatPage'
import Sidebar from './components/layout/Sidebar'
import { attemptSSO } from './services/api'

function ProtectedLayout({ children }) {
  const token = useStore((s) => s.token)
  const location = useLocation()

  if (location.pathname.startsWith('/share/')) {
    const shareId = location.pathname.split('/share/')[1]
    const isShareAuthed = sessionStorage.getItem(`share_authed_${shareId}`)
    if (!token || !isShareAuthed) {
      localStorage.setItem('redirectAfterLogin', location.pathname)
      return <Navigate to="/" replace />
    }
  } else if (!token) {
    return <Navigate to="/" replace />
  }

  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      <Sidebar />
      {children}
    </div>
  )
}

function AdminGuard({ children }) {
  const user = useStore((s) => s.user)
  const isItAdmin = user?.roles?.includes('it_admin')
  if (!isItAdmin) return <Navigate to="/chat" replace />
  return children
}

// Inner component that runs inside BrowserRouter context
function AppRoutes() {
  const setAuth = useStore((s) => s.setAuth)
  const logout = useStore((s) => s.logout)
  const token = useStore((s) => s.token)
  const user = useStore((s) => s.user)
  const [ssoChecked, setSsoChecked] = useState(false)

  useEffect(() => {
    // Case 1: Token exists AND user object loaded (normal active session) → nothing to do
    if (token && user) {
      setSsoChecked(true)
      return
    }

    // Case 2: Token exists in localStorage but user state reset (page refresh)
    if (token && !user) {
      import('./services/api').then(({ fetchMe }) => {
        fetchMe()
          .then((me) => setAuth({ username: me.username, roles: me.roles }, token))
          .catch(() => logout())
          .finally(() => setSsoChecked(true))
      })
      return
    }

    setSsoChecked(true)
  }, [])

  // While SSO check is in progress show a minimal loading indicator
  // BrowserRouter is already mounted above so routing stays intact
  if (!ssoChecked) {
    return (
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        height: '100vh', background: 'var(--bg-0)',
        color: 'var(--text-secondary)', fontFamily: 'var(--font-sans)', fontSize: 13,
      }}>
        <span style={{ opacity: 0.5 }}>Checking Windows authentication…</span>
      </div>
    )
  }

  return (
    <Routes>
      <Route path="/" element={<LoginPage />} />
      <Route
        path="/share/:shareId"
        element={
          <ProtectedLayout>
            <ChatPage />
          </ProtectedLayout>
        }
      />
      <Route
        path="/chat"
        element={
          <ProtectedLayout>
            <ChatPage />
          </ProtectedLayout>
        }
      />
      <Route
        path="/history"
        element={
          <ProtectedLayout>
            <HistoryPage />
          </ProtectedLayout>
        }
      />
      <Route
        path="/admin"
        element={
          <ProtectedLayout>
            <AdminGuard>
              <AdminPage />
            </AdminGuard>
          </ProtectedLayout>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: 'var(--bg-2)',
            color: 'var(--text-primary)',
            border: '1px solid var(--border)',
            fontFamily: 'var(--font-sans)',
            fontSize: 13,
          },
        }}
      />
      <AppRoutes />
    </BrowserRouter>
  )
}
