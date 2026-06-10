// src/pages/AdminPage.jsx
import { useState, useEffect } from 'react'
import { Brain, Trash2, BarChart2, RefreshCw } from 'lucide-react'
import useStore from '../store/useStore'
import { runTraining, runAllTraining, fetchTrainingData, deleteTrainingRecord, fetchFeedbackStats } from '../services/api'
import toast from 'react-hot-toast'

export default function AdminPage() {
  const { instances, user } = useStore()
  const [selectedInst, setSelectedInst] = useState('')
  const [trainingData, setTrainingData] = useState([])
  const [stats, setStats] = useState(null)
  const [loadingTrain, setLoadingTrain] = useState(false)
  const [loadingData, setLoadingData] = useState(false)
  const [selectedIds, setSelectedIds] = useState(new Set())
  const [deletingBulk, setDeletingBulk] = useState(false)

  const adminInstances = instances.filter(() => user?.roles?.some(r => r.endsWith('_admin')))

  const loadData = async (key) => {
    if (!key) return
    setLoadingData(true)
    setSelectedIds(new Set())
    try {
      const [td, st] = await Promise.all([
        fetchTrainingData(key),
        fetchFeedbackStats(key),
      ])
      setTrainingData(td)
      setStats(st)
    } catch {
      toast.error('Failed to load training data')
    } finally {
      setLoadingData(false)
    }
  }

  useEffect(() => { loadData(selectedInst) }, [selectedInst])

  const handleTrain = async (skipSchema = false) => {
    if (!selectedInst) return
    setLoadingTrain(true)
    try {
      await runTraining(selectedInst, skipSchema)
      toast.success('Training started in background')
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Training failed')
    } finally {
      setLoadingTrain(false)
    }
  }

  const handleDelete = async (id) => {
    if (!selectedInst) return
    try {
      await deleteTrainingRecord(selectedInst, id)
      toast.success('Record removed')
      loadData(selectedInst)
    } catch {
      toast.error('Delete failed')
    }
  }

  const handleBulkDelete = async () => {
    if (!selectedInst || selectedIds.size === 0) return
    setDeletingBulk(true)
    try {
      await Promise.all([...selectedIds].map(id => deleteTrainingRecord(selectedInst, id)))
      toast.success(`${selectedIds.size} record${selectedIds.size > 1 ? 's' : ''} removed`)
      loadData(selectedInst)
    } catch {
      toast.error('Bulk delete failed')
    } finally {
      setDeletingBulk(false)
    }
  }

  const toggleRow = (id) => {
    setSelectedIds(prev => {
      const next = new Set(prev)
      next.has(id) ? next.delete(id) : next.add(id)
      return next
    })
  }

  const allChecked = trainingData.length > 0 && selectedIds.size === trainingData.length
  const someChecked = selectedIds.size > 0 && !allChecked

  const toggleAll = () => {
    if (allChecked || someChecked) {
      setSelectedIds(new Set())
    } else {
      setSelectedIds(new Set(trainingData.map(r => r.id)))
    }
  }

  return (
    <div style={styles.page}>
      <header style={styles.header}>
        <h1 style={styles.title}><Brain size={20} style={{ color: 'var(--accent)' }} /> Training & Admin</h1>
      </header>

      <div style={styles.body}>
        {/* Instance picker */}
        <div style={styles.card}>
          <label style={styles.label}>Select Instance</label>
          <select
            style={styles.select}
            value={selectedInst}
            onChange={(e) => setSelectedInst(e.target.value)}
          >
            <option value="">-- choose --</option>
            {adminInstances.map((i) => (
              <option key={i.key} value={i.key}>{i.label}</option>
            ))}
          </select>
        </div>

        {selectedInst && (
          <>
            {/* Feedback stats */}
            {stats && (
              <div style={styles.statsRow}>
                {[
                  ['Total Feedback', stats.total],
                  ['👍 Positive', stats.positive],
                  ['👎 Negative', stats.negative],
                  ['🧠 Auto-Trained', stats.trained_from_feedback],
                ].map(([label, val]) => (
                  <div key={label} style={styles.statCard}>
                    <div style={styles.statVal}>{val}</div>
                    <div style={styles.statLabel}>{label}</div>
                  </div>
                ))}
              </div>
            )}

            {/* Train buttons */}
            <div style={styles.card}>
              <div style={styles.cardTitle}>Run Training</div>
              <div style={styles.btnRow}>
                <button
                  style={{ ...styles.btn, ...styles.btnPrimary, opacity: loadingTrain ? 0.6 : 1 }}
                  onClick={() => handleTrain(false)}
                  disabled={loadingTrain}
                >
                  {loadingTrain ? <RefreshCw size={13} style={{ animation: 'spin 1s linear infinite' }} /> : <Brain size={13} />}
                  Train (schema + Q&A)
                </button>
                <button
                  style={{ ...styles.btn, opacity: loadingTrain ? 0.6 : 1 }}
                  onClick={() => handleTrain(true)}
                  disabled={loadingTrain}
                >
                  Train (Q&A only, skip schema)
                </button>
              </div>
              <p style={styles.hint}>Training runs in background. Refresh the page after a few seconds.</p>
            </div>

            {/* Training data table */}
            <div style={styles.card}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                <div style={styles.cardTitle}>Training Records ({trainingData.length})</div>
                <button style={styles.iconBtn} onClick={() => loadData(selectedInst)}>
                  <RefreshCw size={13} />
                </button>
              </div>

              {/* Bulk action bar */}
              {selectedIds.size > 0 && (
                <div style={styles.bulkBar}>
                  <span style={styles.bulkCount}>{selectedIds.size} selected</span>
                  <button
                    style={{ ...styles.btn, ...styles.btnDanger, opacity: deletingBulk ? 0.6 : 1 }}
                    onClick={handleBulkDelete}
                    disabled={deletingBulk}
                  >
                    <Trash2 size={13} />
                    {deletingBulk ? 'Deleting…' : `Delete ${selectedIds.size} record${selectedIds.size > 1 ? 's' : ''}`}
                  </button>
                </div>
              )}

              {loadingData ? (
                <p style={styles.hint}>Loading…</p>
              ) : trainingData.length === 0 ? (
                <p style={styles.hint}>No training data yet. Run training first.</p>
              ) : (
                <div style={styles.tableWrap}>
                  <table style={styles.table}>
                    <thead>
                      <tr>
                        <th style={{ ...styles.th, width: 36 }}>
                          <input
                            type="checkbox"
                            checked={allChecked}
                            ref={el => { if (el) el.indeterminate = someChecked }}
                            onChange={toggleAll}
                            style={styles.checkbox}
                          />
                        </th>
                        {['Type', 'Content', ''].map((h) => (
                          <th key={h} style={styles.th}>{h}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {trainingData.map((row) => {
                        const isSelected = selectedIds.has(row.id)
                        return (
                          <tr
                            key={row.id}
                            style={isSelected ? styles.trSelected : undefined}
                            onClick={() => toggleRow(row.id)}
                          >
                            <td style={{ ...styles.td, width: 36 }} onClick={e => e.stopPropagation()}>
                              <input
                                type="checkbox"
                                checked={isSelected}
                                onChange={() => toggleRow(row.id)}
                                style={styles.checkbox}
                              />
                            </td>
                            <td style={styles.td}>
                              <span style={{ ...styles.typeTag, ...(typeStyle[row.training_data_type] || {}) }}>
                                {row.training_data_type}
                              </span>
                            </td>
                            <td style={{ ...styles.td, maxWidth: 400 }}>
                              <div style={styles.content}>
                                {row.question || row.content || row.ddl || '—'}
                              </div>
                            </td>
                            <td style={styles.td} onClick={e => e.stopPropagation()}>
                              <button style={styles.deleteBtn} onClick={() => handleDelete(row.id)}>
                                <Trash2 size={12} />
                              </button>
                            </td>
                          </tr>
                        )
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  )
}

const typeStyle = {
  sql: { background: 'rgba(99,179,237,0.15)', color: 'var(--accent)' },
  ddl: { background: 'rgba(245,158,11,0.15)', color: '#f59e0b' },
  documentation: { background: 'rgba(104,211,145,0.15)', color: 'var(--success)' },
}

const styles = {
  page: { flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' },
  header: {
    padding: '16px 24px', borderBottom: '1px solid var(--border)',
    background: 'var(--bg-1)',
  },
  title: { display: 'flex', alignItems: 'center', gap: 10, fontWeight: 600, fontSize: 17 },
  body: { flex: 1, overflowY: 'auto', padding: 24, display: 'flex', flexDirection: 'column', gap: 16 },
  card: {
    background: 'var(--bg-1)', border: '1px solid var(--border)',
    borderRadius: 'var(--radius-lg)', padding: 20,
  },
  cardTitle: { fontWeight: 600, marginBottom: 12 },
  label: { display: 'block', fontSize: 12, color: 'var(--text-secondary)', marginBottom: 8, fontWeight: 600 },
  select: {
    width: '100%', background: 'var(--bg-2)', border: '1px solid var(--border)',
    borderRadius: 'var(--radius)', padding: '8px 12px',
    color: 'var(--text-primary)', fontSize: 13,
  },
  statsRow: { display: 'flex', gap: 12 },
  statCard: {
    flex: 1, background: 'var(--bg-1)', border: '1px solid var(--border)',
    borderRadius: 'var(--radius-lg)', padding: 16, textAlign: 'center',
  },
  statVal: { fontSize: 28, fontWeight: 700, color: 'var(--accent)', fontFamily: 'var(--font-mono)' },
  statLabel: { fontSize: 12, color: 'var(--text-muted)', marginTop: 4 },
  btnRow: { display: 'flex', gap: 10, marginBottom: 10 },
  btn: {
    display: 'flex', alignItems: 'center', gap: 6,
    padding: '9px 16px', borderRadius: 'var(--radius)',
    background: 'var(--bg-3)', border: '1px solid var(--border)',
    color: 'var(--text-primary)', fontSize: 13, fontFamily: 'var(--font-sans)',
    cursor: 'pointer', transition: 'opacity 0.15s',
  },
  btnPrimary: { background: 'var(--accent)', color: '#0a0c10', border: 'none', fontWeight: 600 },
  btnDanger: {
    background: 'rgba(var(--error-rgb, 248,81,73),0.12)',
    border: '1px solid rgba(var(--error-rgb, 248,81,73),0.35)',
    color: 'var(--error)', fontWeight: 600,
  },
  hint: { fontSize: 12, color: 'var(--text-muted)' },
  iconBtn: {
    background: 'var(--bg-3)', border: '1px solid var(--border)',
    borderRadius: 'var(--radius)', padding: '6px 10px',
    color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', cursor: 'pointer',
  },
  bulkBar: {
    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
    padding: '10px 14px', marginBottom: 12,
    background: 'var(--bg-3)', border: '1px solid var(--border)',
    borderRadius: 'var(--radius)',
  },
  bulkCount: { fontSize: 13, color: 'var(--text-secondary)', fontWeight: 500 },
  tableWrap: { overflowX: 'auto', borderRadius: 'var(--radius)', border: '1px solid var(--border)' },
  table: { width: '100%', borderCollapse: 'collapse', fontSize: 12 },
  th: {
    padding: '8px 12px', background: 'var(--bg-3)', color: 'var(--text-secondary)',
    fontWeight: 600, fontSize: 11, textTransform: 'uppercase', letterSpacing: 0.5,
    borderBottom: '1px solid var(--border)', textAlign: 'left',
  },
  td: { padding: '8px 12px', borderBottom: '1px solid var(--border)', color: 'var(--text-primary)', cursor: 'pointer' },
  trSelected: { background: 'rgba(88, 166, 255, 0.07)' },
  checkbox: { cursor: 'pointer', accentColor: 'var(--accent)', width: 13, height: 13 },
  typeTag: {
    display: 'inline-block', padding: '2px 8px', borderRadius: 4,
    fontSize: 11, fontWeight: 600, textTransform: 'uppercase',
  },
  content: {
    maxWidth: 400, overflow: 'hidden', textOverflow: 'ellipsis',
    whiteSpace: 'nowrap', color: 'var(--text-secondary)',
  },
  deleteBtn: {
    background: 'transparent', border: 'none', color: 'var(--error)',
    cursor: 'pointer', padding: 4,
  },
}