// src/App.jsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import useStore from './store/useStore'
import LoginPage from './pages/LoginPage'
import ChatPage from './pages/ChatPage'
import AdminPage from './pages/AdminPage'
import Sidebar from './components/layout/Sidebar'

function ProtectedLayout({ children }) {
  const token = useStore((s) => s.token)
  if (!token) return <Navigate to="/" replace />
  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      <Sidebar />
      {children}
    </div>
  )
}

function AdminGuard({ children }) {
  const user = useStore((s) => s.user)
  const isAdmin = user?.roles?.some((r) => r.endsWith('_admin'))
  if (!isAdmin) return <Navigate to="/chat" replace />
  return children
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
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route
          path="/chat"
          element={
            <ProtectedLayout>
              <ChatPage />
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
    </BrowserRouter>
  )
}