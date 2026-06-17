// src/components/chat/MessageBubble.jsx
import { useState } from 'react'
import { ChevronDown, ChevronRight, Code2, AlertCircle, Paperclip } from 'lucide-react'
import ResultsTable from './ResultsTable'
import FeedbackButtons from '../feedback/FeedbackButtons'

// ── Parse nl_summary into plain text segments and attachment link objects ─────
// The LLM embeds attachment links as:
//   ATTACHMENT_LINK::{"url":"...","label":"..."}
// This function splits the summary into an ordered array of:
//   { type: 'text', content: string }
//   { type: 'attachment', url: string, label: string }
function parseSummary(summary) {
  if (!summary) return []
  const parts = []
  const lines = summary.split('\n')
  for (const line of lines) {
    const trimmed = line.trim()
    if (trimmed.startsWith('ATTACHMENT_LINK::')) {
      try {
        const json = trimmed.slice('ATTACHMENT_LINK::'.length)
        const { url, label } = JSON.parse(json)
        parts.push({ type: 'attachment', url, label })
      } catch {
        // Malformed — fall through and treat as text
        parts.push({ type: 'text', content: line })
      }
    } else {
      parts.push({ type: 'text', content: line })
    }
  }
  // Merge consecutive text lines back into paragraphs
  const merged = []
  for (const part of parts) {
    if (part.type === 'text') {
      if (merged.length > 0 && merged[merged.length - 1].type === 'text') {
        merged[merged.length - 1].content += '\n' + part.content
      } else {
        merged.push({ type: 'text', content: part.content })
      }
    } else {
      merged.push(part)
    }
  }
  return merged.filter(p => !(p.type === 'text' && p.content.trim() === ''))
}

export default function MessageBubble({ message }) {
  const [sqlOpen, setSqlOpen] = useState(false)
  const isUser = message.role === 'user'

  if (isUser) {
    return (
      <div style={styles.userRow}>
        <div style={styles.userBubble}>{message.question}</div>
      </div>
    )
  }

  const summaryParts = parseSummary(message.nl_summary)

  // Assistant bubble
  return (
    <div style={styles.assistantRow}>
      <div style={styles.assistantBubble}>
        {/* Error state */}
        {message.error && <ErrorBox error={message.error} sql={message.sql} />}

        {/* Loading */}
        {message.loading && (
          <div style={styles.loading}>
            <span style={styles.dot} />
            <span style={styles.dot} />
            <span style={styles.dot} />
          </div>
        )}

        {/* NL Summary — text segments + attachment link cards */}
        {summaryParts.length > 0 && !message.loading && (
          <div style={styles.nlSummary}>
            {summaryParts.map((part, i) =>
              part.type === 'attachment' ? (
                <AttachmentLink key={i} url={part.url} label={part.label} />
              ) : (
                <span key={i} style={{ whiteSpace: 'pre-wrap' }}>{part.content}</span>
              )
            )}
          </div>
        )}

        {/* SQL collapsible */}
        {message.sql && !message.loading && (
          <>
            <button style={styles.sqlToggle} onClick={() => setSqlOpen(!sqlOpen)}>
              {sqlOpen ? <ChevronDown size={13} /> : <ChevronRight size={13} />}
              <Code2 size={13} />
              <span>Generated SQL</span>
            </button>
            {sqlOpen && (
              <pre style={styles.sqlBlock}>{message.sql.trim()}</pre>
            )}
          </>
        )}

        {/* Results */}
        {message.results && !message.loading && (
          <ResultsTable results={message.results} />
        )}

        {/* Feedback */}
        {!message.loading && !message.error && message.sql && (
          <FeedbackButtons
            messageId={message.id}
            question={message.question}
            sql={message.sql}
          />
        )}
      </div>
    </div>
  )
}

// ── Attachment link card ───────────────────────────────────────────────────────
function AttachmentLink({ url, label }) {
  return (
    <a
      href={url}
      target="_blank"
      rel="noopener noreferrer"
      style={att.card}
      onMouseEnter={e => {
        e.currentTarget.style.borderColor = 'var(--accent)'
        e.currentTarget.style.background = 'var(--bg-1)'
      }}
      onMouseLeave={e => {
        e.currentTarget.style.borderColor = 'var(--border)'
        e.currentTarget.style.background = 'var(--bg-2)'
      }}
    >
      <Paperclip size={13} style={{ flexShrink: 0, color: 'var(--accent)' }} />
      <span style={att.label}>{label}</span>
      <span style={att.open}>Open ↗</span>
    </a>
  )
}

const att = {
  card: {
    display: 'flex', alignItems: 'center', gap: 8,
    padding: '8px 12px', marginTop: 8,
    background: 'var(--bg-2)', border: '1px solid var(--border)',
    borderRadius: 'var(--radius)', textDecoration: 'none',
    transition: 'border-color 0.15s, background 0.15s',
    cursor: 'pointer',
  },
  label: {
    flex: 1, fontSize: 13, color: 'var(--text-primary)',
    overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
  },
  open: { fontSize: 11, color: 'var(--accent)', flexShrink: 0 },
}

const dotKeyframes = `
@keyframes blink {
  0%, 80%, 100% { opacity: 0.2; transform: scale(0.8); }
  40% { opacity: 1; transform: scale(1); }
}
`

// Inject keyframes once
if (typeof document !== 'undefined' && !document.getElementById('dot-kf')) {
  const s = document.createElement('style')
  s.id = 'dot-kf'
  s.textContent = dotKeyframes
  document.head.appendChild(s)
}

// ── ErrorBox: renders multi-line error messages with a tip line highlighted ──
function ErrorBox({ error, sql }) {
  const [sqlOpen, setSqlOpen] = useState(false)
  const parts = error.split(/\n\n/)
  const mainMessage = parts[0]
  const tipLine = parts.slice(1).join('\n\n').trim()

  return (
    <div style={eb.box}>
      <div style={eb.header}>
        <AlertCircle size={15} style={{ flexShrink: 0, marginTop: 1 }} />
        <span style={eb.main}>{mainMessage}</span>
      </div>

      {tipLine && (
        <div style={eb.tip}>{tipLine}</div>
      )}

      {/* Show the blocked SQL if present, so dev can see what was generated */}
      {sql && (
        <div style={{ marginTop: 8 }}>
          <button style={eb.sqlToggle} onClick={() => setSqlOpen(!sqlOpen)}>
            <Code2 size={11} /> {sqlOpen ? 'Hide' : 'Show'} generated SQL
          </button>
          {sqlOpen && <pre style={eb.sqlBlock}>{sql.trim()}</pre>}
        </div>
      )}
    </div>
  )
}

const eb = {
  box: {
    background: 'var(--error-dim)', border: '1px solid rgba(252,129,129,0.25)',
    borderRadius: 'var(--radius)', padding: '12px 14px',
  },
  header: { display: 'flex', alignItems: 'flex-start', gap: 9 },
  main: { color: 'var(--error)', fontSize: 13, lineHeight: 1.55 },
  tip: {
    marginTop: 10, paddingTop: 10,
    borderTop: '1px solid rgba(252,129,129,0.15)',
    color: 'var(--text-secondary)', fontSize: 12, lineHeight: 1.6,
    whiteSpace: 'pre-wrap',
  },
  sqlToggle: {
    display: 'inline-flex', alignItems: 'center', gap: 5,
    marginTop: 4, background: 'transparent', border: 'none',
    color: 'var(--text-muted)', fontSize: 11, cursor: 'pointer',
  },
  sqlBlock: {
    marginTop: 6, background: 'var(--bg-0)', border: '1px solid var(--border)',
    borderRadius: 'var(--radius)', padding: '8px 12px',
    fontSize: 11, color: 'var(--error)', fontFamily: 'var(--font-mono)',
    overflowX: 'auto', whiteSpace: 'pre-wrap', wordBreak: 'break-all',
  },
}

const styles = {
  userRow: { display: 'flex', justifyContent: 'flex-end', marginBottom: 16 },
  userBubble: {
    maxWidth: '70%', padding: '10px 16px',
    background: 'var(--accent)', color: '#0a0c10',
    borderRadius: '14px 14px 4px 14px', fontWeight: 500, fontSize: 13,
  },
  nlSummary: {
    display: 'flex', flexDirection: 'column',
    marginBottom: 14,
    padding: '12px 14px',
    background: 'var(--bg-1)',
    border: '1px solid var(--border)',
    borderLeft: '4px solid var(--accent)',
    borderRadius: '10px',
    color: 'var(--text-primary)',
    fontSize: 14,
    lineHeight: 1.7,
  },
  assistantRow: { display: 'flex', justifyContent: 'flex-start', marginBottom: 16 },
  assistantBubble: {
    maxWidth: '85%', padding: '14px 16px',
    background: 'var(--bg-2)', border: '1px solid var(--border)',
    borderRadius: '4px 14px 14px 14px',
  },
  loading: { display: 'flex', gap: 5, padding: '4px 0' },
  dot: {
    display: 'inline-block', width: 7, height: 7, borderRadius: '50%',
    background: 'var(--text-muted)',
    animation: 'blink 1.2s infinite',
  },
  sqlToggle: {
    display: 'flex', alignItems: 'center', gap: 6,
    background: 'transparent', border: 'none',
    color: 'var(--text-secondary)', fontSize: 12, padding: '2px 0',
    marginBottom: 4, cursor: 'pointer',
  },
  sqlBlock: {
    background: 'var(--bg-0)', border: '1px solid var(--border)',
    borderRadius: 'var(--radius)', padding: '10px 14px',
    fontSize: 12, color: 'var(--accent)', fontFamily: 'var(--font-mono)',
    overflowX: 'auto', marginBottom: 4,
  },
}