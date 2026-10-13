import { STATUS_LABELS } from '../../lib/labels'
import type { ReviewStatus } from '../../types/report'

const STYLE: Record<ReviewStatus, string> = {
  unverified: 'border-amber/40 bg-amber/10 text-amber',
  under_review: 'border-cyan/40 bg-cyan/10 text-cyan',
  confirmed: 'border-ok/40 bg-ok/10 text-ok',
  disputed: 'border-danger/40 bg-danger/10 text-danger',
  resolved: 'border-muted/40 bg-muted/10 text-muted',
}

export function StatusBadge({ status }: { status: ReviewStatus }) {
  return (
    <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium ${STYLE[status]}`}>
      {STATUS_LABELS[status]}
    </span>
  )
}
