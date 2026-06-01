// src/components/feedback/FeedbackButtons.jsx
import { useState } from 'react'
import { ThumbsUp, ThumbsDown, Check } from 'lucide-react'
import { submitFeedback } from '../../services/api'
import useStore from '../../store/useStore'
import toast from 'react-hot-toast'

export default function FeedbackButtons({ messageId, question, sql }) {
  const [submitted, setSubmitted] = useState(null) // 'up' | 'down'
  const [loading, setLoading] = useState(false)
  const { activeInstance, setMessageFeedback } = useStore()

  const handleFeedback = async (thumbsUp) => {
    if (submitted || loading) return
    setLoading(true)
    try {
      const res = await submitFeedback(activeInstance.key, question, sql, thumbsUp)
      setSubmitted(thumbsUp ? 'up' : 'down')
      setMessageFeedback(messageId, thumbsUp ? 'up' : 'down')
      if (thumbsUp && res.trained) {
        toast.success('Thanks! Added to training data ✓', { icon: '🧠' })
      } else if (thumbsUp) {
        toast.success('Positive feedback recorded!')
      } else {
        toast('Negative feedback noted. We\'ll improve!', { icon: '📝' })
      }
    } catch {
      toast.error('Could not submit feedback')
    } finally {
      setLoading(false)
    }
  }

  if (submitted) {
    return (
      <span style={styles.done}>
        <Check size={12} />
        {submitted === 'up' ? 'Helpful – trained!' : 'Feedback noted'}
      </span>
    )
  }

  return (
    <div style={styles.row}>
      <span style={styles.label}>Was this helpful?</span>
      <button
        style={{ ...styles.btn, ...styles.btnUp }}
        onClick={() => handleFeedback(true)}
        disabled={loading}
        title="Thumbs up – add to training"
      >
        <ThumbsUp size={13} />
      </button>
      <button
        style={{ ...styles.btn, ...styles.btnDown }}
        onClick={() => handleFeedback(false)}
        disabled={loading}
        title="Thumbs down – flag for review"
      >
        <ThumbsDown size={13} />
      </button>
    </div>
  )
}

const styles = {
  row: { display: 'flex', alignItems: 'center', gap: 6, marginTop: 10 },
  label: { fontSize: 11, color: 'var(--text-muted)' },
  btn: {
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    width: 28, height: 28, borderRadius: 6, border: '1px solid var(--border)',
    background: 'var(--bg-3)', transition: 'all 0.15s',
  },
  btnUp: { color: 'var(--success)' },
  btnDown: { color: 'var(--error)' },
  done: {
    display: 'inline-flex', alignItems: 'center', gap: 4,
    fontSize: 11, color: 'var(--text-muted)', marginTop: 10,
  },
}