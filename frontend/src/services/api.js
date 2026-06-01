// src/services/api.js – axios client wired to FastAPI backend
import axios from 'axios'

const api = axios.create({ baseURL: 'http://192.168.11.232:8000/api' })

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

export const fetchMe = () => api.get('/auth/me').then(r => r.data)

// ── Instances ─────────────────────────────────────────────────────────────────
export const fetchInstances = () => api.get('/query/instances').then(r => r.data)

// ── Query ─────────────────────────────────────────────────────────────────────
export const askQuestion = (instance_key, question, session_id = 'default') =>
  api.post('/query/ask', { instance_key, question, session_id }).then(r => r.data)

export const fetchHistory = (instance_key, session_id = 'default') =>
  api.get('/query/history', { params: { instance_key, session_id } }).then(r => r.data)

export const clearHistory = (instance_key, session_id = 'default') =>
  api.delete('/query/history', { params: { instance_key, session_id } }).then(r => r.data)

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

export default api