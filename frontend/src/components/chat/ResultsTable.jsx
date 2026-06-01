// src/components/chat/ResultsTable.jsx
export default function ResultsTable({ results }) {
  if (!results || results.length === 0) {
    return <p style={styles.empty}>No rows returned.</p>
  }

  const columns = Object.keys(results[0])

  return (
    <div style={styles.wrapper}>
      <div style={styles.meta}>{results.length} row{results.length !== 1 ? 's' : ''}</div>
      <div style={styles.tableWrap}>
        <table style={styles.table}>
          <thead>
            <tr>
              {columns.map((col) => (
                <th key={col} style={styles.th}>{col}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {results.map((row, i) => (
              <tr key={i} style={i % 2 === 1 ? styles.trAlt : {}}>
                {columns.map((col) => (
                  <td key={col} style={styles.td}>
                    {row[col] === null ? <span style={styles.null}>NULL</span> : String(row[col])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

const styles = {
  wrapper: { marginTop: 12 },
  meta: { fontSize: 11, color: 'var(--text-muted)', marginBottom: 6 },
  tableWrap: { overflowX: 'auto', borderRadius: 'var(--radius)', border: '1px solid var(--border)' },
  table: { width: '100%', borderCollapse: 'collapse', fontSize: 12 },
  th: {
    padding: '8px 12px', textAlign: 'left', background: 'var(--bg-3)',
    color: 'var(--text-secondary)', fontWeight: 600, fontSize: 11,
    textTransform: 'uppercase', letterSpacing: 0.5, whiteSpace: 'nowrap',
    borderBottom: '1px solid var(--border)',
  },
  td: {
    padding: '7px 12px', color: 'var(--text-primary)',
    borderBottom: '1px solid var(--border)', whiteSpace: 'nowrap',
  },
  trAlt: { background: 'rgba(255,255,255,0.02)' },
  null: { color: 'var(--text-muted)', fontStyle: 'italic' },
  empty: { color: 'var(--text-muted)', fontSize: 13, marginTop: 8 },
}