// src/pages/ChatPage.jsx
import { useRef, useEffect, useState } from 'react'
import { Send, Trash2, Database } from 'lucide-react'
import useStore from '../store/useStore'
import { askQuestion, clearHistory } from '../services/api'
import MessageBubble from '../components/chat/MessageBubble'
import toast from 'react-hot-toast'

const SUGGESTED = {
  hr_policies:      ['How many active policies exist?', 'List all leave policies', 'Who approved the latest policy?'],
  hr_salaries:      ['What is the average salary by department?', 'Show all salary band ranges', 'Who earns above their band maximum?'],
  it_meetingsphere: ['How many meetings this month?', 'Which room is most booked?', 'Who are the top 5 organizers?'],
  it_cdxp:           ['Which projects are over budget?', 'Show resource utilisation this month', 'Who is on more than 2 active projects?'],
}

export default function ChatPage() {
  const { activeInstance, messages, addUserMessage, addAssistantMessage, sessionId, resetSession } = useStore()
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const send = async (question) => {
    if (!question.trim() || loading || !activeInstance) return
    setInput('')
    setLoading(true)

    const userMsgId = `msg_${Date.now()}`
    const assistantMsgId = `msg_${Date.now() + 1}`   // ← separate ID

    addUserMessage(userMsgId, question)
    addAssistantMessage(assistantMsgId, { loading: true, question })

    try {
      const data = await askQuestion(activeInstance.key, question, sessionId)
      addAssistantMessage(assistantMsgId, {          // ← use assistantMsgId
        loading: false,
        question: data.question,
        sql: data.sql,
        results: data.results,
        error: data.error,
      })
    } catch (err) {
      addAssistantMessage(assistantMsgId, {          // ← use assistantMsgId
        loading: false,
        question,
        error: err.response?.data?.detail || 'Request failed',
      })
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      send(input)
    }
  }

  const handleClear = async () => {
    if (!activeInstance) return
    await clearHistory(activeInstance.key, sessionId).catch(() => {})
    resetSession()
    toast.success('Session cleared')
  }

  const suggestions = activeInstance ? (SUGGESTED[activeInstance.key] || []) : []

  return (
    <div style={styles.page}>
      {/* Header */}
      <header style={styles.header}>
        <div>
          <div style={styles.headerTitle}>
            <Database size={16} style={{ color: 'var(--accent)' }} />
            {activeInstance ? activeInstance.label : 'Select a database'}
          </div>
          {activeInstance && (
            <div style={styles.headerSub}>{activeInstance.description}</div>
          )}
        </div>
        {messages.length > 0 && (
          <button style={styles.clearBtn} onClick={handleClear}>
            <Trash2 size={13} /> Clear session
          </button>
        )}
      </header>

      {/* Messages */}
      <div style={styles.messages}>
        {!activeInstance && (
          <div style={styles.empty}>
            <span style={styles.emptyIcon}>←</span>
            <span>Select a database from the sidebar to start querying</span>
          </div>
        )}

        {activeInstance && messages.length === 0 && (
          <div style={styles.welcome}>
            <div style={styles.welcomeTitle}>Ask anything about <strong>{activeInstance.label}</strong></div>
            <div style={styles.suggestGrid}>
              {suggestions.map((s) => (
                <button key={s} style={styles.suggest} onClick={() => send(s)}>{s}</button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div style={styles.inputArea}>
        <textarea
          style={styles.textarea}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={activeInstance ? `Ask about ${activeInstance.label}…` : 'Select a database first'}
          disabled={!activeInstance || loading}
          rows={1}
        />
        <button
          style={{ ...styles.sendBtn, opacity: (!input.trim() || loading || !activeInstance) ? 0.4 : 1 }}
          onClick={() => send(input)}
          disabled={!input.trim() || loading || !activeInstance}
        >
          <Send size={15} />
        </button>
      </div>
    </div>
  )
}

const styles = {
  page: {
    flex: 1, display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden',
  },
  header: {
    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
    padding: '16px 24px', borderBottom: '1px solid var(--border)',
    background: 'var(--bg-1)',
  },
  headerTitle: { display: 'flex', alignItems: 'center', gap: 8, fontWeight: 600, fontSize: 15 },
  headerSub: { fontSize: 12, color: 'var(--text-muted)', marginTop: 2 },
  clearBtn: {
    display: 'flex', alignItems: 'center', gap: 6,
    padding: '6px 12px', borderRadius: 'var(--radius)',
    background: 'transparent', border: '1px solid var(--border)',
    color: 'var(--text-muted)', fontSize: 12, transition: 'border-color 0.15s',
  },
  messages: { flex: 1, overflowY: 'auto', padding: '24px', display: 'flex', flexDirection: 'column' },
  empty: {
    flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center',
    gap: 12, color: 'var(--text-muted)', fontSize: 14,
  },
  emptyIcon: { fontSize: 20 },
  welcome: { textAlign: 'center', marginTop: 60 },
  welcomeTitle: { fontSize: 18, marginBottom: 24, color: 'var(--text-secondary)' },
  suggestGrid: { display: 'flex', flexWrap: 'wrap', gap: 10, justifyContent: 'center', maxWidth: 600, margin: '0 auto' },
  suggest: {
    padding: '10px 16px', background: 'var(--bg-2)', border: '1px solid var(--border)',
    borderRadius: 'var(--radius)', color: 'var(--text-secondary)', fontSize: 13,
    cursor: 'pointer', transition: 'border-color 0.15s, color 0.15s',
    textAlign: 'left',
  },
  inputArea: {
    display: 'flex', gap: 10, padding: '16px 24px',
    borderTop: '1px solid var(--border)', background: 'var(--bg-1)',
  },
  textarea: {
    flex: 1, background: 'var(--bg-2)', border: '1px solid var(--border)',
    borderRadius: 'var(--radius)', padding: '10px 14px',
    color: 'var(--text-primary)', fontSize: 14, fontFamily: 'var(--font-sans)',
    resize: 'none', outline: 'none', lineHeight: 1.5,
  },
  sendBtn: {
    width: 42, height: 42, borderRadius: 'var(--radius)',
    background: 'var(--accent)', border: 'none',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    color: '#0a0c10', flexShrink: 0, transition: 'opacity 0.15s',
  },
}