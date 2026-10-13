import { EmptyState, ErrorState, LoadingCards } from '../common/StateViews'
import type { ReportSummary } from '../../types/report'
import { ReportCard } from './ReportCard'

interface ReportFeedProps {
  reports: ReportSummary[] | null
  error: string | null
  selectedId: string | null
  onOpen: (id: string) => void
  onRetry: () => void
}

export function ReportFeed({ reports, error, selectedId, onOpen, onRetry }: ReportFeedProps) {
  if (error && reports === null) {
    return <ErrorState message={`Reports could not be loaded. ${error}`} onRetry={onRetry} retryLabel="Retry loading" />
  }
  if (reports === null) return <LoadingCards />
  if (reports.length === 0) {
    return (
      <EmptyState
        title="No reports yet"
        body="Submit the first report for an area. Each report starts as Unverified until a reviewer changes its status."
      />
    )
  }
  return (
    <div className="space-y-3">
      {error && <ErrorState message={`Latest update failed. ${error}`} onRetry={onRetry} retryLabel="Retry" />}
      {reports.map((report) => (
        <ReportCard key={report.id} report={report} selected={report.id === selectedId} onOpen={onOpen} />
      ))}
    </div>
  )
}
