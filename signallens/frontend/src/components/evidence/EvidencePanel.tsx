import { motion } from 'framer-motion'
import { MapPin, X } from 'lucide-react'
import type { ReportDetail, ReviewStatus } from '../../types/report'
import { ErrorState, LoadingCards } from '../common/StateViews'
import { StatusBadge } from '../reports/StatusBadge'
import { WeatherSection } from '../weather/WeatherSection'
import { PredictionSection } from './PredictionSection'
import { ProvenanceSection } from './ProvenanceSection'
import { ReviewSection } from './ReviewSection'

interface EvidencePanelProps {
  report: ReportDetail | null
  loading: boolean
  error: string | null
  busy: boolean
  onClose: () => void
  onRetryLoad: () => void
  onClassify: () => void
  onRefreshWeather: () => void
  onStatusChange: (status: ReviewStatus, note?: string) => void
}

/** Right-hand drawer on desktop, bottom sheet on phones. Sections keep prediction, context, provenance and review apart. */
export function EvidencePanel(props: EvidencePanelProps) {
  const { report, loading, error, busy, onClose, onRetryLoad, onClassify, onRefreshWeather, onStatusChange } = props

  return (
    <>
      <motion.div
        className="fixed inset-0 z-40 bg-canvas/70 backdrop-blur-sm lg:bg-transparent lg:backdrop-blur-none"
        onClick={onClose}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        aria-hidden
      />
      <motion.aside
        role="dialog"
        aria-modal="true"
        aria-label="Report evidence"
        className="fixed inset-x-0 bottom-0 z-50 flex max-h-[88dvh] flex-col rounded-t-3xl border border-border bg-canvas shadow-2xl lg:inset-y-0 lg:bottom-auto lg:left-auto lg:right-0 lg:h-dvh lg:max-h-none lg:w-[34rem] lg:rounded-none lg:rounded-l-3xl"
        initial={{ y: 40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ type: 'spring', stiffness: 320, damping: 32 }}
      >
        <header className="flex items-start justify-between gap-3 border-b border-border px-5 py-4">
          <div className="min-w-0">
            <p className="text-[11px] uppercase tracking-[0.14em] text-muted">Report evidence</p>
            {report ? (
              <>
                <h2 className="mt-1 line-clamp-2 text-base font-semibold text-ink">{report.description}</h2>
                <p className="mt-1 flex items-center gap-1 text-xs text-muted">
                  <MapPin aria-hidden size={12} /> {report.location_label}
                </p>
              </>
            ) : (
              <h2 className="mt-1 text-base font-semibold text-ink">Loading report</h2>
            )}
          </div>
          <div className="flex shrink-0 items-center gap-2">
            {report && <StatusBadge status={report.status} />}
            <button
              type="button"
              onClick={onClose}
              aria-label="Close evidence panel"
              className="grid size-9 place-items-center rounded-xl border border-border text-muted hover:text-ink"
            >
              <X aria-hidden size={16} />
            </button>
          </div>
        </header>

        <div className="flex-1 space-y-4 overflow-y-auto px-5 py-5">
          {loading && !report && <LoadingCards count={2} />}
          {error && !report && <ErrorState message={error} onRetry={onRetryLoad} retryLabel="Retry loading" />}

          {report && (
            <>
              {report.freshness === 'stale' && (
                <p className="rounded-xl border border-muted/40 bg-muted/10 px-3 py-2 text-xs text-muted">
                  This report is older than the freshness threshold. Check whether the situation still applies.
                </p>
              )}
              <PredictionSection predictions={report.predictions} busy={busy} onClassify={onClassify} />
              <WeatherSection weather={report.weather} busy={busy} onRefresh={onRefreshWeather} />
              <ProvenanceSection report={report} />
              <ReviewSection report={report} busy={busy} onChange={onStatusChange} />
            </>
          )}
        </div>
      </motion.aside>
    </>
  )
}
