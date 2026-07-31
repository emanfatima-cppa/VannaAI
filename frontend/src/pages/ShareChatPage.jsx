// src/pages/ShareChatPage.jsx
import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { fetchSharedChat, forkSharedChat } from '../services/api'
import useStore from '../store/useStore'
import { MessageCircle, Share2, ArrowRight, CornerDownRight, Database, User, Calendar, CheckCircle2 } from 'lucide-react'
import toast from 'react-hot-toast'

export default function ShareChatPage() {
  const { shareId } = useParams()
  const navigate = useNavigate()
  const [chatData, setChatData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [forking, setForking] = useState(false)
  const { user, setActiveInstance } = useStore()

  useEffect(() => {
    async function loadSharedChat() {
      setLoading(true)
      try {
        const data = await fetchSharedChat(shareId)
        setChatData(data)
      } catch (err) {
        toast.error(err.response?.data?.detail || 'Shared chat not found or link expired')
      } finally {
        setLoading(false)
      }
    }
    if (shareId) loadSharedChat()
  }, [shareId])

  const handleContinueChat = async () => {
    if (!user) {
      toast('Please log in to continue this chat conversation', { icon: '🔑' })
      navigate('/login')
      return
    }

    setForking(true)
    try {
      const result = await forkSharedChat(shareId)
      if (result.instance_key) {
        setActiveInstance(result.instance_key)
      }
      toast.success('Chat loaded! You can now ask follow-up questions.')
      navigate('/chat')
    } catch (err) {
      toast.error('Failed to continue shared chat')
    } finally {
      setForking(false)
    }
  }

  if (loading) {
    return (
      <div style={styles.loadingPage}>
        <div style={styles.spinner} />
        <p style={{ color: 'var(--text-secondary)', marginTop: 16 }}>Loading shared conversation...</p>
      </div>
    )
  }

  if (!chatData) {
    return (
      <div style={styles.emptyPage}>
        <Share2 size={48} style={{ color: 'var(--text-muted)', marginBottom: 16 }} />
        <h2 style={{ color: 'var(--text-primary)', marginBottom: 8 }}>Shared Chat Not Found</h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: 24 }}>This share link may have expired or is invalid.</p>
        <button style={styles.primaryBtn} onClick={() => navigate('/')}>Go to Dashboard</button>
      </div>
    )
  }

  return (
    <div style={styles.page}>
      {/* Header Banner */}
      <header style={styles.header}>
        <div style={styles.headerInfo}>
          <div style={styles.titleRow}>
            <Share2 size={20} style={{ color: 'var(--accent)' }} />
            <h1 style={styles.headerTitle}>{chatData.title || 'Shared Chat Conversation'}</h1>
          </div>
          <div style={styles.metaRow}>
            <span><User size={13} inline /> Shared by: <strong>{chatData.owner_username}</strong></span>
            <span><Database size={13} inline /> Database: <strong>{chatData.instance_key}</strong></span>
            <span><Calendar size={13} inline /> {chatData.created_at ? new Date(chatData.created_at).toLocaleDateString() : 'Recent'}</span>
          </div>
        </div>

        <button style={styles.continueBtn} onClick={handleContinueChat} disabled={forking}>
          {forking ? 'Loading...' : 'Continue this Chat'}
          <ArrowRight size={16} />
        </button>
      </header>

      {/* Messages Feed */}
      <main style={styles.content}>
        <div style={styles.messagesContainer}>
          {chatData.messages && chatData.messages.length > 0 ? (
            chatData.messages.map((msg, idx) => {
              const questionText = msg.question || (msg.role === 'user' ? msg.text : null)
              const isUser = Boolean(questionText)

              if (isUser) {
                return (
                  <div key={idx} style={styles.userBubbleWrapper}>
                    <div style={styles.userBubble}>
                      <p style={styles.userText}>{questionText}</p>
                    </div>
                  </div>
                )
              }

              return (
                <div key={idx} style={styles.assistantCard}>
                  <div style={styles.assistantHeader}>
                    <span style={styles.assistantBadge}>Cortexa AI Response</span>
                  </div>

                  {msg.sql && (
                    <div style={styles.sqlBox}>
                      <div style={styles.sqlHeader}>Generated SQL Query</div>
                      <pre style={styles.sqlCode}>{msg.sql}</pre>
                    </div>
                  )}

                  {msg.nl_summary && (
                    <div style={styles.summaryBox}>
                      <p style={styles.summaryText}>{msg.nl_summary}</p>
                    </div>
                  )}

                  {msg.error && (
                    <div style={styles.errorBox}>
                      <p style={styles.errorText}>Error: {msg.error}</p>
                    </div>
                  )}
                </div>
              )
            })
          ) : (
            <p style={{ color: 'var(--text-secondary)', textAlign: 'center', marginTop: 40 }}>No messages in this shared snapshot.</p>
          )}
        </div>
      </main>

      {/* Bottom Floating Prompt */}
      <div style={styles.bottomBar}>
        <div style={styles.bottomBarContent}>
          <span>Want to ask follow-up questions on this data?</span>
          <button style={styles.bottomBtn} onClick={handleContinueChat}>
            Continue Chat as {user ? user.username : 'User'}
            <CornerDownRight size={14} />
          </button>
        </div>
      </div>
    </div>
  )
}

const styles = {
  page: {
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    background: 'var(--bg-0)',
    color: 'var(--text-primary)',
  },
  loadingPage: {
    height: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', background: 'var(--bg-0)',
  },
  emptyPage: {
    height: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', background: 'var(--bg-0)', padding: 24, textAlign: 'center',
  },
  spinner: {
    width: 32, height: 32, border: '3px solid var(--border)', borderTop: '3px solid var(--accent)', borderRadius: '50%', animation: 'spin 1s linear infinite',
  },
  header: {
    display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '20px 32px',
    background: 'var(--bg-1)', borderBottom: '1px solid var(--border)', flexWrap: 'wrap', gap: 16,
  },
  headerInfo: { display: 'flex', flexDirection: 'column', gap: 6 },
  titleRow: { display: 'flex', alignItems: 'center', gap: 10 },
  headerTitle: { fontSize: 18, fontWeight: 700, color: 'var(--text-primary)', margin: 0 },
  metaRow: { display: 'flex', alignItems: 'center', gap: 18, fontSize: 12, color: 'var(--text-secondary)' },
  continueBtn: {
    display: 'flex', alignItems: 'center', gap: 8, padding: '10px 20px',
    background: 'var(--accent)', color: '#ffffff', border: 'none', borderRadius: 'var(--radius)',
    fontWeight: 600, fontSize: 13, cursor: 'pointer', transition: 'all 0.15s ease',
  },
  primaryBtn: {
    padding: '10px 20px', background: 'var(--accent)', color: '#ffffff', border: 'none', borderRadius: 'var(--radius)', fontWeight: 600, cursor: 'pointer',
  },
  content: { flex: 1, padding: '32px 24px 100px 24px', maxWidth: 900, margin: '0 auto', width: '100%' },
  messagesContainer: { display: 'flex', flexDirection: 'column', gap: 20 },
  userBubbleWrapper: { display: 'flex', justifyContent: 'flex-end' },
  userBubble: {
    maxWidth: '80%', padding: '12px 18px', borderRadius: '16px 16px 4px 16px',
    background: 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)', color: '#ffffff', boxShadow: '0 2px 8px rgba(79, 70, 229, 0.2)',
  },
  userText: { margin: 0, fontSize: 14, lineHeight: 1.5 },
  assistantCard: {
    background: 'var(--bg-1)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)',
    padding: 20, display: 'flex', flexDirection: 'column', gap: 14, boxShadow: 'var(--shadow)',
  },
  assistantHeader: { display: 'flex', alignItems: 'center', justifyContent: 'space-between' },
  assistantBadge: { fontSize: 11, fontWeight: 700, color: 'var(--accent)', textTransform: 'uppercase', letterSpacing: 0.5 },
  sqlBox: {
    background: 'var(--bg-2)', border: '1px solid var(--border)', borderLeft: '4px solid var(--accent)', borderRadius: 'var(--radius)', padding: 12,
  },
  sqlHeader: { fontSize: 11, fontWeight: 700, color: 'var(--accent)', marginBottom: 6 },
  sqlCode: { margin: 0, fontSize: 12, fontFamily: 'var(--font-mono)', color: 'var(--text-primary)', whiteSpace: 'pre-wrap' },
  summaryBox: { fontSize: 14, color: 'var(--text-primary)', lineHeight: 1.6 },
  summaryText: { margin: 0 },
  errorBox: { padding: 12, background: 'var(--error-dim)', border: '1px solid var(--error)', borderRadius: 'var(--radius)' },
  errorText: { margin: 0, color: 'var(--error)', fontSize: 13 },
  bottomBar: {
    position: 'fixed', bottom: 0, left: 0, right: 0, background: 'var(--bg-1)', borderTop: '1px solid var(--border)', padding: '14px 24px', zIndex: 100,
  },
  bottomBarContent: {
    maxWidth: 900, margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: 13, color: 'var(--text-secondary)',
  },
  bottomBtn: {
    display: 'flex', alignItems: 'center', gap: 6, padding: '8px 16px', background: 'var(--bg-2)', border: '1px solid var(--border)',
    borderRadius: 'var(--radius)', color: 'var(--text-primary)', fontSize: 13, fontWeight: 600, cursor: 'pointer',
  },
}
