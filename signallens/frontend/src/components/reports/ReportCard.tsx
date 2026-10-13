import { motion } from 'framer-motion'
import { Clock, FlaskConical, MapPin } from 'lucide-react'
import { percent, timeAgo } from '../../lib/format'
import { CATEGORY_LABELS, SOURCE_LABELS } from '../../lib/labels'
import type { ReportSummary } from '../../types/report'
import { StatusBadge } from './StatusBadge'

interface ReportCardProps {
  report: ReportSummary
  selected: boolean
  onOpen: (id: string) => void
}

export function ReportCard({ report, selected, onOpen }: ReportCardProps) {
  const category = report.category ? (CATEGORY_LABELS[report.category] ?? report.category) : null

  return (
    <motion.button
      type="button"
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      onClick={() => onOpen(report.id)}
      aria-pressed={selected}
      className={`w-full rounded-2xl border p-4 text-left transition-colors ${
        selected ? 'border-cyan/60 bg-surface-2' : 'border-border bg-surface hover:border-cyan/30'
      }`}
    >
      <div className="flex items-center justify-between gap-3">
        <StatusBadge status={report.status} />
        {report.freshness === 'stale' && (
          <span className="rounded-full border border-muted/40 px-2 py-0.5 text-xs text-muted">Stale</span>
        )}
      </div>

      <p className="mt-3 line-clamp-2 text-sm leading-relaxed text-ink">{report.description}</p>

      {category ? (
        <p className="mt-3 flex flex-wrap items-center gap-x-1.5 text-xs text-muted">
          <FlaskConical aria-hidden size={13} />
          <span>AI prediction:</span>
          <span className="text-ink">{category}</span>
          {report.category_score !== null && <span>· model score {percent(report.category_score)}</span>}
        </p>
      ) : (
        <p className="mt-3 text-xs text-muted">No model result yet</p>
      )}

      <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-muted">
        <span className="inline-flex items-center gap-1">
          <MapPin aria-hidden size={12} />
          {report.location_label}
        </span>
        <span className="inline-flex items-center gap-1">
          <Clock aria-hidden size={12} />
          {timeAgo(report.created_at)}
        </span>
        <span>{SOURCE_LABELS[report.source_type]}</span>
      </div>
    </motion.button>
  )
}
