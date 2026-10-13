import { useState } from 'react'
import { formatUtc } from '../../lib/format'
import { STATUS_LABELS } from '../../lib/labels'
import { ALLOWED_NEXT } from '../../lib/status'
import type { ReportDetail, ReviewStatus } from '../../types/report'
import { Section } from '../common/Section'
import { StatusBadge } from '../reports/StatusBadge'

interface ReviewSectionProps {
  report: ReportDetail
  busy: boolean
  onChange: (status: ReviewStatus, note?: string) => void
}

export function ReviewSection({ report, busy, onChange }: ReviewSectionProps) {
  const [note, setNote] = useState('')
  const options = ALLOWED_NEXT[report.status]

  return (
    <Section
      kicker="Human review"
      title="Review status"
      note="Status changes only through these explicit actions. This prototype has no reviewer accounts, so a change here is not an authoritative review."
      tone="review"
    >
      <div className="flex flex-wrap items-center gap-3">
        <span className="text-sm text-muted">Current status</span>
        <StatusBadge status={report.status} />
      </div>

      {report.review_note && (
        <p className="rounded-xl bg-canvas/50 p-3 text-sm text-ink">
          <span className="text-muted">Note: </span>
          {report.review_note}
        </p>
      )}

      <div className="space-y-1.5">
        <label htmlFor="review-note" className="text-xs font-medium text-muted">
          Note for this change (optional)
        </label>
        <input
          id="review-note"
          value={note}
          onChange={(event) => setNote(event.target.value)}
          maxLength={200}
          placeholder="e.g. Confirmed by a second, independent source"
          className="w-full rounded-xl border border-border bg-canvas px-3 py-2 text-sm text-ink placeholder:text-muted/70 focus:border-cyan/60 focus:outline-none"
        />
      </div>

      <div className="flex flex-wrap gap-2">
        {options.map((status) => (
          <button
            key={status}
            type="button"
            disabled={busy}
            onClick={() => {
              onChange(status, note.trim() || undefined)
              setNote('')
            }}
            className="rounded-xl border border-border px-3 py-2 text-sm text-ink hover:border-ok/50 hover:bg-ok/10 disabled:opacity-60"
          >
            Set to {STATUS_LABELS[status]}
          </button>
        ))}
      </div>

      <p className="text-xs text-muted">Last status change: {formatUtc(report.updated_at)}</p>
    </Section>
  )
}
