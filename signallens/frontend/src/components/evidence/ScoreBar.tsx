import { motion } from 'framer-motion'
import { percent } from '../../lib/format'

interface ScoreBarProps {
  value: number
  label?: string
}

/** A model score, drawn as a bar. The caption makes clear it is not a probability that an incident happened. */
export function ScoreBar({ value, label = 'Model score' }: ScoreBarProps) {
  const clamped = Math.min(1, Math.max(0, value))
  return (
    <div className="space-y-1.5">
      <div className="flex justify-between text-xs text-muted">
        <span>{label}</span>
        <span className="tabular-nums text-ink">{percent(clamped)}</span>
      </div>
      <div
        role="meter"
        aria-label={label}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={Math.round(clamped * 100)}
        className="h-2 overflow-hidden rounded-full bg-surface-2"
      >
        <motion.div
          className="h-full rounded-full"
          style={{ background: 'linear-gradient(90deg, var(--color-cyan), var(--color-amber))' }}
          initial={{ width: 0 }}
          animate={{ width: `${clamped * 100}%` }}
          transition={{ duration: 0.6, ease: 'easeOut' }}
        />
      </div>
      <p className="text-[11px] leading-relaxed text-muted">
        Confidence in this label from the model. It is not the probability that an incident happened.
      </p>
    </div>
  )
}
