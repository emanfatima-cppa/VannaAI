// src/pages/HistoryPage.jsx
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  History,
  Search,
  Trash2,
  Database,
  User,
  Clock,
  Code,
  CheckCircle2,
  XCircle,
  Copy,
  Check,
  Play,
  RefreshCw,
  Filter,
  Download,
  Calendar,
  FileText,
  ChevronDown,
} from 'lucide-react'
import { fetchUserHistory, clearUserHistory } from '../services/api'
import useStore from '../store/useStore'
import toast from 'react-hot-toast'

export default function HistoryPage() {
  const navigate = useNavigate()
  const { user, instances, setActiveInstance } = useStore()
  const [historyItems, setHistoryItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [selectedInstance, setSelectedInstance] = useState('ALL')
  const [dateFilter, setDateFilter] = useState('ALL')
  const [copiedId, setCopiedId] = useState(null)
  const [exportDropdownOpen, setExportDropdownOpen] = useState(false)

  const loadHistory = async () => {
    setLoading(true)
    try {
      const data = await fetchUserHistory(
        selectedInstance === 'ALL' ? null : selectedInstance
      )
      setHistoryItems(data)
    } catch (err) {
      toast.error('Failed to load query history')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadHistory()
  }, [selectedInstance])

  const handleClearHistory = async () => {
    if (!window.confirm('Are you sure you want to clear your saved query history from the database?')) {
      return
    }
    try {
      await clearUserHistory(selectedInstance === 'ALL' ? null : selectedInstance)
      toast.success('Query history cleared')
      setHistoryItems([])
    } catch (err) {
      toast.error('Failed to clear history')
    }
  }

  const handleCopySql = (id, sqlText) => {
    if (!sqlText) return
    navigator.clipboard.writeText(sqlText)
    setCopiedId(id)
    toast.success('SQL copied to clipboard')
    setTimeout(() => setCopiedId(null), 2000)
  }

  const handleRunQueryAgain = (item) => {
    const inst = instances.find((i) => i.key === item.instance_key)
    if (inst) {
      setActiveInstance(inst)
      navigate('/chat')
    } else {
      toast.error(`Database '${item.instance_key}' not accessible`)
    }
  }

  const handleDownloadHistory = (format = 'pdf') => {
    if (!filtered || filtered.length === 0) {
      toast.error('No query history available for export')
      return
    }

    const dateStr = new Date().toISOString().split('T')[0]
    const dbTag = selectedInstance === 'ALL' ? 'All Databases' : (instanceMap[selectedInstance] || selectedInstance)

    if (format === 'word') {
      try {
        const itemsHtml = filtered.map((item, idx) => `
          <div style="margin-bottom: 20px; padding: 14px; border: 1px solid #d1d5db; border-radius: 6px; background-color: #ffffff;">
            <p style="font-size: 10pt; color: #6b7280; margin: 0 0 6px 0;">
              <strong>#${idx + 1} | Time:</strong> ${item.created_at || 'N/A'} | <strong>Database:</strong> ${instanceMap[item.instance_key] || item.instance_key}
            </p>
            <p style="font-size: 12pt; color: #111827; margin: 0 0 8px 0;">
              <strong>Question:</strong> ${item.question}
            </p>
            <div style="background-color: #f3f4f6; padding: 10px; border-left: 4px solid #8b5cf6; font-family: 'Courier New', monospace; font-size: 10pt; margin-bottom: 8px;">
              <strong>Generated SQL Query:</strong><br/>
              <pre style="margin: 4px 0 0 0; white-space: pre-wrap; font-family: 'Courier New', monospace;">${item.sql || 'No SQL generated'}</pre>
            </div>
            <p style="font-size: 11pt; color: #1f2937; margin: 0;">
              <strong>Answer / Summary:</strong> ${item.nl_summary || item.error || 'N/A'}
            </p>
          </div>
        `).join('')

        const docHtml = `<html xmlns:o='urn:schemas-microsoft-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-microsoft-com:office:word' xmlns='http://www.w3.org/TR/REC-html40'>
        <head>
          <meta charset='utf-8'>
          <title>Query History Log</title>
          <style>
            body { font-family: Calibri, Arial, sans-serif; margin: 20px; color: #111827; }
            h2 { color: #6d28d9; margin-bottom: 4px; }
            p.sub { color: #4b5563; font-size: 11pt; margin-bottom: 20px; }
          </style>
        </head>
        <body>
          <h2>CPPA AI Assistant - Query History Report</h2>
          <p class="sub"><strong>Target Database:</strong> ${dbTag} | <strong>Export Date:</strong> ${dateStr} | <strong>Total Queries:</strong> ${filtered.length}</p>
          <hr style="border: 0; border-top: 1px solid #e5e7eb; margin-bottom: 20px;"/>
          ${itemsHtml}
        </body>
        </html>`

        const blob = new Blob(['\ufeff' + docHtml], { type: 'application/msword' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `Query_History_${dateStr}.doc`
        document.body.appendChild(a)
        a.click()
        setTimeout(() => {
          if (document.body.contains(a)) document.body.removeChild(a)
          URL.revokeObjectURL(url)
        }, 100)
        toast.success(`Downloaded ${filtered.length} queries as Word file (.doc)`)
      } catch (err) {
        toast.error('Failed to export Word document')
      }
    } else if (format === 'pdf') {
      const toastId = toast.loading('Generating PDF file...')

      try {
        const jspdfModule = window.jspdf
        if (!jspdfModule || !jspdfModule.jsPDF) {
          toast.error('PDF library loading... please try again in a moment', { id: toastId })
          return
        }

        const doc = new jspdfModule.jsPDF({
          orientation: 'portrait',
          unit: 'mm',
          format: 'a4',
        })

        const pageWidth = doc.internal.pageSize.width
        const pageHeight = doc.internal.pageSize.height
        const margin = 14
        const contentWidth = pageWidth - (margin * 2)

        // Header Title
        doc.setFont('helvetica', 'bold')
        doc.setFontSize(16)
        doc.setTextColor(109, 40, 217)
        doc.text('CPPA AI Assistant - Query History Report', margin, 18)

        // Subtitle
        doc.setFont('helvetica', 'normal')
        doc.setFontSize(9)
        doc.setTextColor(100, 116, 139)
        doc.text(`Target Database: ${dbTag}  |  Export Date: ${dateStr}  |  Total Queries: ${filtered.length}`, margin, 25)

        // Divider Line
        doc.setDrawColor(203, 213, 225)
        doc.setLineWidth(0.5)
        doc.line(margin, 28, pageWidth - margin, 28)

        let y = 36

        filtered.forEach((item, idx) => {
          // Check if space left on page
          if (y > pageHeight - 35) {
            doc.addPage()
            y = 20
          }

          // Item Meta Header
          doc.setFontSize(9)
          doc.setFont('helvetica', 'bold')
          doc.setTextColor(100, 116, 139)
          const metaStr = `#${idx + 1} | Time: ${item.created_at || 'N/A'} | Database: ${instanceMap[item.instance_key] || item.instance_key}`
          doc.text(metaStr, margin, y)
          y += 5

          // User Question
          doc.setFontSize(11)
          doc.setFont('helvetica', 'bold')
          doc.setTextColor(15, 23, 42)
          const qLines = doc.splitTextToSize(`Question: ${item.question}`, contentWidth)
          doc.text(qLines, margin, y)
          y += (qLines.length * 5) + 3

          // Generated SQL Box
          if (item.sql) {
            doc.setFontSize(8.5)
            doc.setFont('courier', 'normal')
            
            const rawSqlLines = doc.splitTextToSize(item.sql.trim(), contentWidth - 10)
            const boxHeight = (rawSqlLines.length * 4) + 10

            // Check if SQL box fits on page
            if (y + boxHeight > pageHeight - 20) {
              doc.addPage()
              y = 20
            }

            // Light gray box background
            doc.setFillColor(248, 250, 252)
            doc.setDrawColor(203, 213, 225)
            doc.rect(margin, y, contentWidth, boxHeight, 'F')
            doc.rect(margin, y, contentWidth, boxHeight, 'S')

            // Left accent bar (purple)
            doc.setFillColor(124, 58, 237)
            doc.rect(margin, y, 2.5, boxHeight, 'F')

            // SQL Label
            doc.setFont('helvetica', 'bold')
            doc.setFontSize(8.5)
            doc.setTextColor(109, 40, 217)
            doc.text('Generated SQL Query:', margin + 5, y + 5)

            // SQL text
            doc.setFont('courier', 'normal')
            doc.setFontSize(8.5)
            doc.setTextColor(15, 23, 42)
            doc.text(rawSqlLines, margin + 5, y + 10)

            y += boxHeight + 4
          }

          // Answer / Summary
          doc.setFontSize(9.5)
          doc.setFont('helvetica', 'normal')
          doc.setTextColor(51, 65, 85)
          const ansText = `Answer / Summary: ${item.nl_summary || item.error || 'N/A'}`
          const ansLines = doc.splitTextToSize(ansText, contentWidth)

          if (y + (ansLines.length * 4.5) > pageHeight - 20) {
            doc.addPage()
            y = 20
          }

          doc.text(ansLines, margin, y)
          y += (ansLines.length * 4.5) + 8

          // Item Separator Line
          doc.setDrawColor(226, 232, 240)
          doc.line(margin, y - 4, pageWidth - margin, y - 4)
        })

        doc.save(`Query_History_${dateStr}.pdf`)
        toast.success(`Downloaded ${filtered.length} queries as PDF`, { id: toastId })
      } catch (e) {
        toast.error('Failed to generate PDF file', { id: toastId })
      }
    }
  }

  // Filter items by search prompt, SQL, and date range
  const filtered = historyItems.filter((item) => {
    const q = search.toLowerCase()
    const matchesSearch = (
      item.question.toLowerCase().includes(q) ||
      (item.sql && item.sql.toLowerCase().includes(q)) ||
      item.instance_key.toLowerCase().includes(q)
    )

    if (!matchesSearch) return false
    if (dateFilter === 'ALL') return true

    if (!item.created_at) return true
    const itemDate = new Date(item.created_at)
    const now = new Date()

    if (dateFilter === 'TODAY') {
      return itemDate.toDateString() === now.toDateString()
    } else if (dateFilter === 'YESTERDAY') {
      const yesterday = new Date(now)
      yesterday.setDate(now.getDate() - 1)
      return itemDate.toDateString() === yesterday.toDateString()
    } else if (dateFilter === '7DAYS') {
      const diffTime = Math.abs(now - itemDate)
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
      return diffDays <= 7
    } else if (dateFilter === '30DAYS') {
      const diffTime = Math.abs(now - itemDate)
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
      return diffDays <= 30
    }
    return true
  })

  // Helper map for instance labels
  const instanceMap = (instances || []).reduce((acc, cur) => {
    acc[cur.key] = cur.label
    return acc
  }, {})

  return (
    <div style={styles.container}>
      {/* Top Header */}
      <header style={styles.header}>
        <div>
          <div style={styles.headerTitle}>
            <History size={16} style={{ color: 'var(--accent)' }} />
            Query History
          </div>
          <div style={styles.headerSub}>
            Saved query logs for user <strong>{user?.username}</strong> in PostgreSQL database
          </div>
        </div>

        <div style={styles.headerRight}>
          {historyItems.length > 0 && (
            <button style={styles.clearBtn} onClick={handleClearHistory}>
              <Trash2 size={14} /> Clear History
            </button>
          )}
        </div>
      </header>

      {/* Controls Bar */}
      <div style={styles.controlsBar}>
        {/* Search */}
        <div style={styles.searchWrapper}>
          <Search size={16} style={styles.searchIcon} />
          <input
            type="text"
            style={styles.searchInput}
            placeholder="Search queries, SQL, or database tags..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          {search && (
            <button style={styles.clearSearchBtn} onClick={() => setSearch('')}>
              ×
            </button>
          )}
        </div>

        {/* Date Range Filter */}
        <div style={styles.filterWrapper}>
          <Calendar size={14} style={{ color: 'var(--text-muted)' }} />
          <select
            style={styles.select}
            value={dateFilter}
            onChange={(e) => setDateFilter(e.target.value)}
          >
            <option value="ALL">All Dates</option>
            <option value="TODAY">Today</option>
            <option value="YESTERDAY">Yesterday</option>
            <option value="7DAYS">Last 7 Days</option>
            <option value="30DAYS">Last 30 Days</option>
          </select>
        </div>

        {/* Database Filter */}
        <div style={styles.filterWrapper}>
          <Filter size={14} style={{ color: 'var(--text-muted)' }} />
          <select
            style={styles.select}
            value={selectedInstance}
            onChange={(e) => setSelectedInstance(e.target.value)}
          >
            <option value="ALL">All Databases</option>
            {instances.map((inst) => (
              <option key={inst.key} value={inst.key}>
                {inst.label}
              </option>
            ))}
          </select>
        </div>

        {/* Unified Export Dropdown */}
        <div style={{ position: 'relative', marginLeft: 'auto' }}>
          <button
            style={styles.exportDropdownBtn}
            onClick={() => setExportDropdownOpen(!exportDropdownOpen)}
            disabled={filtered.length === 0}
          >
            <Download size={14} /> Export <ChevronDown size={13} style={{ marginLeft: 2 }} />
          </button>

          {exportDropdownOpen && (
            <div style={styles.exportMenu} onClick={() => setExportDropdownOpen(false)}>
              <button
                style={styles.exportMenuItem}
                onClick={() => handleDownloadHistory('pdf')}
              >
                <FileText size={14} style={{ color: '#8b5cf6' }} /> Export as PDF (.pdf)
              </button>
              <button
                style={styles.exportMenuItem}
                onClick={() => handleDownloadHistory('word')}
              >
                <Download size={14} style={{ color: '#3b82f6' }} /> Export as Word (.doc)
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Content Area */}
      <div style={styles.content}>
        {loading ? (
          <div style={styles.stateCard}>
            <RefreshCw size={24} style={{ color: 'var(--accent)' }} className="spin" />
            <p style={{ marginTop: 12, color: 'var(--text-secondary)' }}>Loading query history from database...</p>
          </div>
        ) : filtered.length === 0 ? (
          <div style={styles.stateCard}>
            <History size={36} style={{ color: 'var(--text-muted)', opacity: 0.5 }} />
            <h3 style={{ marginTop: 12, fontSize: 16, color: 'var(--text-primary)' }}>No queries found</h3>
            <p style={{ marginTop: 4, fontSize: 13, color: 'var(--text-muted)' }}>
              {search
                ? 'No history matches your search filter.'
                : 'Queries you ask CPPA AI Assistant will be automatically saved to your history here.'}
            </p>
          </div>
        ) : (
          <div style={styles.grid}>
            {filtered.map((item) => (
              <div key={item.id} style={styles.card}>
                {/* Card Header */}
                <div style={styles.cardHeader}>
                  <div style={styles.tagGroup}>
                    <span style={styles.dbTag}>
                      <Database size={12} />
                      {instanceMap[item.instance_key] || item.instance_key}
                    </span>
                    <span style={item.status === 'error' ? styles.statusError : styles.statusSuccess}>
                      {item.status === 'error' ? (
                        <>
                          <XCircle size={12} /> Failed
                        </>
                      ) : (
                        <>
                          <CheckCircle2 size={12} /> Success
                        </>
                      )}
                    </span>
                  </div>

                  <div style={styles.metaGroup}>
                    <span style={styles.metaItem}>
                      <User size={12} /> {item.username}
                    </span>
                    <span style={styles.metaItem}>
                      <Clock size={12} /> {formatTimestamp(item.created_at)}
                    </span>
                  </div>
                </div>

                {/* Question */}
                <div style={styles.questionText}>
                  "{item.question}"
                </div>

                {/* Summary if present */}
                {item.nl_summary && (
                  <div style={styles.summaryBox}>
                    {item.nl_summary}
                  </div>
                )}

                {/* Error if present */}
                {item.error && (
                  <div style={styles.errorBox}>
                    <strong>Error:</strong> {item.error}
                  </div>
                )}

                {/* SQL Box */}
                {item.sql && (
                  <div style={styles.sqlBox}>
                    <div style={styles.sqlHeader}>
                      <span style={styles.sqlTitle}>
                        <Code size={13} /> Generated SQL
                      </span>
                      <button
                        style={styles.copyBtn}
                        onClick={() => handleCopySql(item.id, item.sql)}
                        title="Copy SQL"
                      >
                        {copiedId === item.id ? (
                          <>
                            <Check size={12} style={{ color: 'var(--success)' }} /> Copied
                          </>
                        ) : (
                          <>
                            <Copy size={12} /> Copy
                          </>
                        )}
                      </button>
                    </div>
                    <pre style={styles.sqlCode}>{item.sql}</pre>
                  </div>
                )}

                {/* Card Footer Actions */}
                <div style={styles.cardFooter}>
                  <button style={styles.reRunBtn} onClick={() => handleRunQueryAgain(item)}>
                    <Play size={13} /> Ask in Chat
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function formatTimestamp(isoStr) {
  if (!isoStr) return ''
  try {
    const d = new Date(isoStr)
    return d.toLocaleString(undefined, {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return isoStr
  }
}

const styles = {
  container: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    height: '100vh',
    overflow: 'hidden',
    background: 'var(--bg-0)',
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '16px 24px',
    background: 'var(--bg-1)',
    borderBottom: '1px solid var(--border)',
  },
  headerTitle: {
    display: 'flex',
    alignItems: 'center',
    gap: 8,
    fontWeight: 600,
    fontSize: 15,
    color: 'var(--text-primary)',
  },
  headerSub: {
    fontSize: 12,
    color: 'var(--text-secondary)',
    marginTop: 2,
    fontWeight: 400,
  },
  headerRight: {
    display: 'flex',
    gap: 10,
  },
  refreshBtn: {
    display: 'flex',
    alignItems: 'center',
    gap: 6,
    padding: '8px 14px',
    borderRadius: 'var(--radius)',
    background: 'var(--bg-2)',
    border: '1px solid var(--border)',
    color: 'var(--text-secondary)',
    fontSize: 13,
    fontWeight: 500,
    cursor: 'pointer',
    transition: 'all 0.15s',
  },
  clearBtn: {
    display: 'flex',
    alignItems: 'center',
    gap: 6,
    padding: '8px 14px',
    borderRadius: 'var(--radius)',
    background: 'rgba(239, 68, 68, 0.1)',
    border: '1px solid rgba(239, 68, 68, 0.25)',
    color: '#ef4444',
    fontSize: 13,
    fontWeight: 500,
    cursor: 'pointer',
    transition: 'all 0.15s',
  },
  controlsBar: {
    display: 'flex',
    gap: 16,
    padding: '14px 28px',
    background: 'var(--bg-1)',
    borderBottom: '1px solid var(--border)',
    alignItems: 'center',
  },
  searchWrapper: {
    flex: 1,
    position: 'relative',
    display: 'flex',
    alignItems: 'center',
  },
  searchIcon: {
    position: 'absolute',
    left: 12,
    color: 'var(--text-muted)',
    pointerEvents: 'none',
  },
  searchInput: {
    width: '100%',
    padding: '8px 32px 8px 36px',
    background: 'var(--bg-2)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius)',
    color: 'var(--text-primary)',
    fontSize: 13,
    outline: 'none',
  },
  clearSearchBtn: {
    position: 'absolute',
    right: 10,
    background: 'transparent',
    border: 'none',
    color: 'var(--text-muted)',
    fontSize: 16,
    cursor: 'pointer',
  },
  filterWrapper: {
    display: 'flex',
    alignItems: 'center',
    gap: 8,
    background: 'var(--bg-2)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius)',
    padding: '0 12px',
  },
  select: {
    background: 'transparent',
    border: 'none',
    color: 'var(--text-secondary)',
    fontSize: 13,
    padding: '8px 0',
    outline: 'none',
    cursor: 'pointer',
  },
  exportDropdownBtn: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: 6,
    padding: '7px 16px',
    borderRadius: 'var(--radius)',
    background: 'var(--accent)',
    color: '#ffffff',
    fontSize: 13,
    fontWeight: 600,
    border: 'none',
    cursor: 'pointer',
    boxShadow: '0 2px 8px rgba(109, 40, 217, 0.25)',
    transition: 'all 0.15s ease',
  },
  exportMenu: {
    position: 'absolute',
    top: 'calc(100% + 6px)',
    right: 0,
    background: 'var(--bg-1)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius)',
    boxShadow: '0 8px 24px rgba(0,0,0,0.25)',
    zIndex: 100,
    minWidth: 180,
    overflow: 'hidden',
    display: 'flex',
    flexDirection: 'column',
    padding: '4px 0',
  },
  exportMenuItem: {
    display: 'flex',
    alignItems: 'center',
    gap: 8,
    padding: '10px 14px',
    background: 'transparent',
    border: 'none',
    color: 'var(--text-primary)',
    fontSize: 13,
    fontWeight: 500,
    cursor: 'pointer',
    textAlign: 'left',
    width: '100%',
    transition: 'background 0.15s ease',
  },
  content: {
    flex: 1,
    overflowY: 'auto',
    padding: '24px 28px',
  },
  stateCard: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '60px 20px',
    textAlign: 'center',
  },
  grid: {
    display: 'flex',
    flexDirection: 'column',
    gap: 16,
    maxWidth: 960,
    margin: '0 auto',
  },
  card: {
    background: 'var(--bg-1)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius)',
    padding: '18px 20px',
    display: 'flex',
    flexDirection: 'column',
    gap: 12,
    boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
    transition: 'border-color 0.15s',
  },
  cardHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    flexWrap: 'wrap',
    gap: 8,
  },
  tagGroup: {
    display: 'flex',
    alignItems: 'center',
    gap: 8,
  },
  dbTag: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: 6,
    padding: '4px 10px',
    borderRadius: '12px',
    background: 'var(--accent-dim)',
    color: 'var(--accent)',
    fontSize: 11,
    fontWeight: 600,
  },
  statusSuccess: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: 4,
    padding: '4px 10px',
    borderRadius: '12px',
    background: 'rgba(34, 197, 94, 0.12)',
    color: '#22c55e',
    fontSize: 11,
    fontWeight: 600,
  },
  statusError: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: 4,
    padding: '4px 10px',
    borderRadius: '12px',
    background: 'rgba(239, 68, 68, 0.12)',
    color: '#ef4444',
    fontSize: 11,
    fontWeight: 600,
  },
  metaGroup: {
    display: 'flex',
    alignItems: 'center',
    gap: 14,
  },
  metaItem: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: 5,
    fontSize: 11,
    color: 'var(--text-muted)',
  },
  questionText: {
    fontSize: 15,
    fontWeight: 600,
    color: 'var(--text-primary)',
    lineHeight: 1.4,
  },
  summaryBox: {
    fontSize: 13,
    color: 'var(--text-secondary)',
    background: 'var(--bg-2)',
    padding: '10px 14px',
    borderRadius: 'var(--radius)',
    lineHeight: 1.5,
  },
  errorBox: {
    fontSize: 12,
    color: '#ef4444',
    background: 'rgba(239, 68, 68, 0.08)',
    border: '1px solid rgba(239, 68, 68, 0.2)',
    padding: '8px 12px',
    borderRadius: 'var(--radius)',
  },
  sqlBox: {
    background: 'var(--bg-0)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius)',
    overflow: 'hidden',
  },
  sqlHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '6px 12px',
    background: 'var(--bg-2)',
    borderBottom: '1px solid var(--border)',
  },
  sqlTitle: {
    display: 'flex',
    alignItems: 'center',
    gap: 6,
    fontSize: 11,
    fontWeight: 600,
    color: 'var(--text-muted)',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  copyBtn: {
    display: 'flex',
    alignItems: 'center',
    gap: 4,
    background: 'transparent',
    border: 'none',
    color: 'var(--text-muted)',
    fontSize: 11,
    cursor: 'pointer',
    padding: '2px 6px',
    borderRadius: '4px',
  },
  sqlCode: {
    margin: 0,
    padding: '12px 14px',
    fontSize: 12,
    fontFamily: 'var(--font-mono)',
    color: '#80caff',
    overflowX: 'auto',
    whiteSpace: 'pre-wrap',
    lineHeight: 1.5,
  },
  cardFooter: {
    display: 'flex',
    justifyContent: 'flex-end',
    paddingTop: 4,
  },
  reRunBtn: {
    display: 'flex',
    alignItems: 'center',
    gap: 6,
    padding: '6px 14px',
    borderRadius: 'var(--radius)',
    background: 'var(--accent-dim)',
    border: '1px solid var(--accent)',
    color: 'var(--accent)',
    fontSize: 12,
    fontWeight: 600,
    cursor: 'pointer',
    transition: 'all 0.15s',
  },
}
