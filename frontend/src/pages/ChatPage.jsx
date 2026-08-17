// src/pages/ChatPage.jsx
import { useRef, useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { Send, Trash2, Database, ChevronUp, ChevronDown, Share2, Copy, Check } from 'lucide-react'
import useStore from '../store/useStore'
import { askQuestion, clearHistory, createShareLink, fetchSharedChat } from '../services/api'
import MessageBubble from '../components/chat/MessageBubble'
import toast from 'react-hot-toast'

const SUGGESTED = {
  hr_policies:      ['How many active policies exist?', 'List all leave policies', 'Who approved the latest policy?'],
  hr_salaries:      ['What is the average salary by department?', 'Show all salary band ranges', 'Who earns above their band maximum?'],
  it_meetingsphere: ['How many meetings this month?', 'Which room is most booked?', 'Who are the top 5 organizers?'],
  it_cdxp:           ['Which projects are over budget?', 'Show resource utilisation this month', 'Who is on more than 2 active projects?'],
  it_rms:            ['What is the total number of records in the RMS database?', 'Show all active records', 'Who last modified a specific record?'],
  it_pop:            ['Tell me the total number of invoices not yet verified', 'How many Diary Incomplete exist', 'Give me the list of all IPPs'],
}

export default function ChatPage() {
  const { shareId } = useParams()
  const { instances, activeInstance, setActiveInstance, messages, setMessages, addUserMessage, addAssistantMessage, sessionId, resetSession } = useStore()
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [showScrollTop, setShowScrollTop] = useState(false)
  const [showScrollBottom, setShowScrollBottom] = useState(false)

  // Share Modal State
  const [shareModalOpen, setShareModalOpen] = useState(false)
  const [shareUrl, setShareUrl] = useState('')
  const [sharing, setSharing] = useState(false)
  const [copied, setCopied] = useState(false)

  const bottomRef = useRef(null)
  const containerRef = useRef(null)
  const inputRef = useRef(null)

  // Load shared chat if URL has /share/:shareId
  useEffect(() => {
    if (shareId) {
      fetchSharedChat(shareId).then((data) => {
        if (data && data.instance_key) {
          const inst = instances.find((i) => i.key === data.instance_key) || {
            key: data.instance_key,
            label: data.instance_key.toUpperCase(),
            description: `Shared Database (${data.instance_key})`,
          }
          setActiveInstance(inst)
          if (data.messages && Array.isArray(data.messages)) {
            setMessages(data.messages)
          }
          toast.success(`Loaded shared chat by ${data.owner_username}`)
        }
      }).catch(() => {
        toast.error('Shared chat link expired or not found')
      })
    }
  }, [shareId, instances])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Global Ctrl+K shortcut listener to focus query input
  useEffect(() => {
    const handleGlobalKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault()
        inputRef.current?.focus()
      }
    }
    window.addEventListener('keydown', handleGlobalKeyDown)
    return () => window.removeEventListener('keydown', handleGlobalKeyDown)
  }, [])

  const handleScroll = () => {
    if (!containerRef.current) return
    const { scrollTop, scrollHeight, clientHeight } = containerRef.current
    setShowScrollTop(scrollTop > 200)
    setShowScrollBottom(scrollTop + clientHeight < scrollHeight - 150)
  }

  const scrollToTop = () => {
    containerRef.current?.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const scrollToBottom = () => {
    containerRef.current?.scrollTo({ top: containerRef.current.scrollHeight, behavior: 'smooth' })
  }

  useEffect(() => {
    if (activeInstance && !loading) {
      setTimeout(() => inputRef.current?.focus(), 50)
    }
  }, [activeInstance, loading])

  const handleShareChat = async () => {
    if (!activeInstance || messages.length === 0) {
      toast.error('No conversation to share')
      return
    }
    setSharing(true)
    try {
      const data = await createShareLink(activeInstance.key, messages)
      const fullUrl = `${window.location.origin}/share/${data.share_id}`
      setShareUrl(fullUrl)
      setShareModalOpen(true)
      setCopied(false)
    } catch (err) {
      toast.error('Failed to generate share link')
    } finally {
      setSharing(false)
    }
  }

  const handleCopyLink = () => {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(shareUrl)
      } else {
        const textarea = document.createElement('textarea')
        textarea.value = shareUrl
        textarea.style.position = 'fixed'
        textarea.style.left = '-9999px'
        textarea.style.top = '-9999px'
        document.body.appendChild(textarea)
        textarea.focus()
        textarea.select()
        document.execCommand('copy')
        document.body.removeChild(textarea)
      }
      setCopied(true)
      toast.success('Share link copied to clipboard!')
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      toast.error('Failed to copy. Please select link text to copy.')
    }
  }

  const send = async (question) => {
    if (!question.trim() || loading || !activeInstance) return
    setInput('')
    setLoading(true)

    const userMsgId = `msg_${Date.now()}`
    const assistantMsgId = `msg_${Date.now() + 1}`

    addUserMessage(userMsgId, question)
    addAssistantMessage(assistantMsgId, { loading: true, question })

    try {
      const data = await askQuestion(activeInstance.key, question, sessionId)
      addAssistantMessage(assistantMsgId, {
        loading: false,
        question: data.question,
        sql: data.sql,
        results: data.results,
        error: data.error,
        nl_summary: data.nl_summary,
      })
    } catch (err) {
      addAssistantMessage(assistantMsgId, {
        loading: false,
        question,
        error: err.response?.data?.detail || 'Request failed',
      })
    } finally {
      setLoading(false)
      setTimeout(() => inputRef.current?.focus(), 50)
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
    setTimeout(() => inputRef.current?.focus(), 50)
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
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <button style={styles.shareBtn} onClick={handleShareChat} disabled={sharing}>
              <Share2 size={13} /> {sharing ? 'Creating Link...' : 'Share Chat'}
            </button>
            <button style={styles.clearBtn} onClick={handleClear}>
              <Trash2 size={13} /> Clear session
            </button>
          </div>
        )}
      </header>

      {/* Messages Wrapper */}
      <div style={styles.messagesWrapper}>
        <div style={styles.messages} ref={containerRef} onScroll={handleScroll}>
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

        {/* Floating Scroll Controls */}
        <div style={styles.floatingControls}>
          {showScrollTop && (
            <button style={styles.scrollBtn} onClick={scrollToTop} title="Scroll to Top">
              <ChevronUp size={16} />
            </button>
          )}
          {showScrollBottom && (
            <button style={styles.scrollBtn} onClick={scrollToBottom} title="Scroll to Bottom">
              <ChevronDown size={16} />
            </button>
          )}
        </div>
      </div>

      {/* Input */}
      <div style={styles.inputArea}>
        <div style={styles.inputWrapper}>
          <textarea
            ref={inputRef}
            style={styles.textarea}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={activeInstance ? `Ask Anything…` : 'Select a database first'}
            disabled={!activeInstance || loading}
            rows={1}
          />
        </div>
        <button
          style={{ ...styles.sendBtn, opacity: (!input.trim() || loading || !activeInstance) ? 0.4 : 1 }}
          onClick={() => send(input)}
          disabled={!input.trim() || loading || !activeInstance}
        >
          <Send size={15} />
        </button>
      </div>

      {/* Share Modal */}
      {shareModalOpen && (
        <div style={styles.modalOverlay} onClick={() => setShareModalOpen(false)}>
          <div style={styles.modalCard} onClick={(e) => e.stopPropagation()}>
            <div style={styles.modalHeader}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontWeight: 600, fontSize: 15, color: 'var(--text-primary)' }}>
                <Share2 size={16} style={{ color: 'var(--accent)' }} />
                Share Chat Link
              </div>
              <button style={styles.modalCloseBtn} onClick={() => setShareModalOpen(false)}>×</button>
            </div>
            <div style={{ padding: '18px 20px' }}>
              <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 14, lineHeight: 1.5 }}>
                Anyone with this link can view this snapshot of the chat conversation and ask follow-up questions.
              </p>
              <div style={{ display: 'flex', gap: 8 }}>
                <input
                  type="text"
                  readOnly
                  value={shareUrl}
                  style={styles.modalInput}
                  onClick={(e) => e.target.select()}
                />
                <button style={styles.copyBtn} onClick={handleCopyLink}>
                  {copied ? <Check size={14} /> : <Copy size={14} />}
                  {copied ? 'Copied!' : 'Copy'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
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
  headerTitle: { display: 'flex', alignItems: 'center', gap: 8, fontWeight: 600, fontSize: 15, color: 'var(--text-primary)' },
  headerSub: { fontSize: 12, color: 'var(--text-secondary)', marginTop: 2, fontWeight: 400 },
  shareBtn: {
    display: 'flex', alignItems: 'center', gap: 6,
    padding: '6px 14px', borderRadius: 'var(--radius)',
    background: 'var(--accent-dim)', border: '1px solid var(--accent)',
    color: 'var(--accent)', fontSize: 12, fontWeight: 600, cursor: 'pointer', transition: 'all 0.15s ease',
  },
  clearBtn: {
    display: 'flex', alignItems: 'center', gap: 6,
    padding: '6px 14px', borderRadius: 'var(--radius)',
    background: 'transparent', border: 'none',
    color: 'var(--error)', fontSize: 13, fontWeight: 500, cursor: 'pointer', transition: 'all 0.15s ease',
  },
  messagesWrapper: {
    flex: 1, position: 'relative', overflow: 'hidden', display: 'flex', flexDirection: 'column',
  },
  messages: { flex: 1, overflowY: 'auto', padding: '24px', display: 'flex', flexDirection: 'column' },
  empty: {
    flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center',
    gap: 12, color: 'var(--text-secondary)', fontSize: 14,
  },
  emptyIcon: { fontSize: 20 },
  welcome: { textAlign: 'center', marginTop: 60 },
  welcomeTitle: { fontSize: 18, marginBottom: 24, color: 'var(--text-primary)', fontWeight: 600 },
  suggestGrid: { display: 'flex', flexWrap: 'wrap', gap: 10, justifyContent: 'center', maxWidth: 600, margin: '0 auto' },
  suggest: {
    padding: '10px 16px', background: 'var(--bg-2)', border: '1px solid var(--border)',
    borderRadius: 'var(--radius)', color: 'var(--text-primary)', fontSize: 13, fontWeight: 500,
    cursor: 'pointer', transition: 'all 0.15s ease',
    textAlign: 'left', boxShadow: '0 1px 4px rgba(0,0,0,0.05)',
  },
  floatingControls: {
    position: 'absolute', bottom: 20, right: 24, display: 'flex', flexDirection: 'column', gap: 8, zIndex: 10,
  },
  scrollBtn: {
    width: 36, height: 36, borderRadius: '50%', background: 'var(--bg-2)', border: '1px solid var(--border)',
    color: 'var(--text-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center',
    boxShadow: 'var(--shadow)', cursor: 'pointer', transition: 'all 0.2s ease',
  },
  inputArea: {
    display: 'flex', gap: 10, padding: '16px 24px',
    borderTop: '1px solid var(--border)', background: 'var(--bg-1)',
  },
  inputWrapper: {
    flex: 1, position: 'relative', display: 'flex', alignItems: 'center',
  },
  textarea: {
    width: '100%', background: 'var(--bg-2)', border: '1px solid var(--border)',
    borderRadius: 'var(--radius)', padding: '10px 20px 10px 14px',
    color: 'var(--text-primary)', fontSize: 14, fontFamily: 'var(--font-sans)',
    resize: 'none', outline: 'none', lineHeight: 1.5,
  },
  shortcutHint: {
    position: 'absolute', right: 12, padding: '2px 6px', background: 'var(--bg-3)',
    borderRadius: 4, color: 'var(--text-secondary)', fontSize: 11, fontWeight: 600,
    fontFamily: 'var(--font-mono)', pointerEvents: 'none',
  },
  sendBtn: {
    width: 42, height: 42, borderRadius: 'var(--radius)',
    background: 'var(--accent)', border: 'none',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    color: '#ffffff', flexShrink: 0, transition: 'opacity 0.15s', cursor: 'pointer',
  },
  modalOverlay: {
    position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)',
    display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: 20,
  },
  modalCard: {
    width: '100%', maxWidth: 480, background: 'var(--bg-1)', border: '1px solid var(--border)',
    borderRadius: 'var(--radius-lg)', boxShadow: '0 20px 25px -5px rgba(0,0,0,0.3)', overflow: 'hidden',
  },
  modalHeader: {
    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
    padding: '14px 20px', borderBottom: '1px solid var(--border)', background: 'var(--bg-2)',
  },
  modalCloseBtn: {
    background: 'none', border: 'none', fontSize: 20, color: 'var(--text-secondary)', cursor: 'pointer',
  },
  modalInput: {
    flex: 1, padding: '8px 12px', background: 'var(--bg-2)', border: '1px solid var(--border)',
    borderRadius: 'var(--radius)', color: 'var(--text-primary)', fontSize: 13, fontFamily: 'var(--font-mono)', outline: 'none',
  },
  copyBtn: {
    display: 'flex', alignItems: 'center', gap: 6, padding: '8px 16px',
    background: 'var(--accent)', color: '#ffffff', border: 'none', borderRadius: 'var(--radius)',
    fontSize: 13, fontWeight: 600, cursor: 'pointer', flexShrink: 0,
  },
}