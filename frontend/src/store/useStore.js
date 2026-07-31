// src/store/useStore.js
import { create } from 'zustand'

const useStore = create((set, get) => ({
  // ── Auth ───────────────────────────────────────────────────────────────────
  user: null,
  token: localStorage.getItem('token') || null,
  setAuth: (user, token) => {
    localStorage.setItem('token', token)
    set({ user, token })
  },
  logout: () => {
    localStorage.removeItem('token')
    set({ user: null, token: null, activeInstance: null, messages: [] })
  },

  // ── DB Instance selection ─────────────────────────────────────────────────
  instances: [],
  activeInstance: null,
  setInstances: (instances) => set({ instances }),
  setActiveInstance: (inst) => set({ activeInstance: inst, messages: [] }),

  // ── Chat messages ─────────────────────────────────────────────────────────
  // messages: [{ id, role: 'user'|'assistant', question, sql, results, error, loading }]
  messages: [],
  setMessages: (messages) => set({ messages }),
  sessionId: `session_${Date.now()}`,

  addUserMessage: (id, question) => {
  set((s) => ({
    messages: [...s.messages, { id, role: 'user', question }],
  }))
},

  addAssistantMessage: (id, data) => {
    set((s) => {
      const existing = s.messages.find((m) => m.id === id)
      if (existing) {
        return {
          messages: s.messages.map((m) =>
            m.id === id ? { ...m, ...data, role: 'assistant' } : m
          ),
        }
      }
      return { messages: [...s.messages, { id, role: 'assistant', ...data }] }
    })
  },

  setMessageFeedback: (id, feedback) => {
    set((s) => ({
      messages: s.messages.map((m) => (m.id === id ? { ...m, feedback } : m)),
    }))
  },

  resetSession: () => set({ messages: [], sessionId: `session_${Date.now()}` }),

  // ── Loading ───────────────────────────────────────────────────────────────
  isLoading: false,
  setLoading: (v) => set({ isLoading: v }),

  // ── Theme ──────────────────────────────────────────────────────────────────
  theme: (() => {
    const saved = localStorage.getItem('theme') || 'dark'
    if (typeof document !== 'undefined') {
      document.documentElement.setAttribute('data-theme', saved)
    }
    return saved
  })(),
  setTheme: (theme) => {
    localStorage.setItem('theme', theme)
    if (typeof document !== 'undefined') {
      document.documentElement.setAttribute('data-theme', theme)
    }
    set({ theme })
  },
  toggleTheme: () => {
    const currentTheme = get().theme
    const nextTheme = currentTheme === 'dark' ? 'light' : 'dark'
    get().setTheme(nextTheme)
  },

  // ── Admin panel ───────────────────────────────────────────────────────────
  adminTab: 'training',
  setAdminTab: (t) => set({ adminTab: t }),
}))

export default useStore