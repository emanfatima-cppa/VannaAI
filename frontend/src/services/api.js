// src/services/api.js – axios client wired to FastAPI backend
import axios from 'axios'

const api = axios.create({ baseURL: 'http://192.168.11.232:8001/api' })

// Attach JWT on every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// ── Auth ──────────────────────────────────────────────────────────────────────
export const login = async (username, password) => {
  const form = new URLSearchParams({ username, password })
  const { data } = await api.post('/auth/login', form, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
  return data
}

export const loginWindows = async (username, password, domain = '.') => {
  const { data } = await api.post('/auth/windows-login', { username, password, domain })
  return data
}

export const fetchMe = () => api.get('/auth/me').then(r => r.data)
export const logoutUser = () => api.post('/auth/logout').then(r => r.data)

/**
 * attemptSSO — silently tries Windows Negotiate (Kerberos/NTLM) SSO.
 * 
 * How it works:
 * - Calls GET /api/auth/sso using fetch (NOT axios) with credentials:'include'
 *   so the browser can attach its Windows Kerberos/NTLM token automatically.
 * - On Trusted Sites / Local Intranet: browser sends the token → SSO succeeds → returns JWT user data
 * - On local dev / non-Trusted Site: browser won't send token → returns null → manual popup shown
 */
export const attemptSSO = async () => {
  try {
    // Use native fetch with credentials so browser attaches Negotiate token automatically
    const baseUrl = api.defaults.baseURL.replace('/api', '')
    const res = await fetch(`${baseUrl}/api/auth/sso`, {
      method: 'GET',
      credentials: 'include',  // ← this lets browser send Kerberos/NTLM token
    })
    if (res.ok) {
      const data = await res.json()
      return data  // { access_token, username, roles, sso: true }
    }
    return null  // 401 = not on Trusted Site, fall back to manual popup
  } catch {
    return null  // Network error or SSO not available
  }
}


// ── Instances ─────────────────────────────────────────────────────────────────
export const fetchInstances = () => api.get('/query/instances').then(r => r.data)

// ── Query ─────────────────────────────────────────────────────────────────────
export const askQuestion = (instance_key, question, session_id = 'default') =>
  api.post('/query/ask', { instance_key, question, session_id }).then(r => r.data)

export const fetchHistory = (instance_key, session_id = 'default') =>
  api.get('/query/history', { params: { instance_key, session_id } }).then(r => r.data)

export const clearHistory = (instance_key, session_id = 'default') =>
  api.delete('/query/history', { params: { instance_key, session_id } }).then(r => r.data)

export const fetchUserHistory = (instance_key = null, limit = 100) =>
  api.get('/query/user-history', { params: { instance_key, limit } }).then(r => r.data)

export const clearUserHistory = (instance_key = null) =>
  api.delete('/query/user-history', { params: { instance_key } }).then(r => r.data)


// ── Feedback ──────────────────────────────────────────────────────────────────
export const submitFeedback = (instance_key, question, sql, thumbs_up, comment = '') =>
  api.post('/query/feedback', { instance_key, question, sql, thumbs_up, comment }).then(r => r.data)

// ── Training (admin) ──────────────────────────────────────────────────────────
export const runTraining = (instance_key, skip_schema = false) =>
  api.post('/training/run', { instance_key, skip_schema }).then(r => r.data)

export const runAllTraining = (skip_schema = false) =>
  api.post('/training/run-all', null, { params: { skip_schema } }).then(r => r.data)

export const fetchTrainingData = (instance_key) =>
  api.get(`/training/data/${instance_key}`).then(r => r.data)

export const deleteTrainingRecord = (instance_key, training_id) =>
  api.delete(`/training/data/${instance_key}/${training_id}`).then(r => r.data)

export const fetchFeedbackStats = (instance_key) =>
  api.get(`/training/feedback/stats/${instance_key}`).then(r => r.data)

// ── Share Chat ────────────────────────────────────────────────────────────────
export const createShareLink = (instance_key, messages, title = null) =>
  api.post('/share/create', { instance_key, messages, title }).then(r => r.data)

export const fetchSharedChat = (shareId) =>
  api.get(`/share/${shareId}`).then(r => r.data)

export const forkSharedChat = (shareId) =>
  api.post('/share/fork', { share_id: shareId }).then(r => r.data)

export default api