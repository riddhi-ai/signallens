import { useCallback, useEffect, useState } from 'react'
import { Toaster, toast } from 'react-hot-toast'
import { api } from './api/client'
import { EvidencePanel } from './components/evidence/EvidencePanel'
import { Header } from './components/layout/Header'
import { PrototypeBanner } from './components/layout/PrototypeBanner'
import { ReportFeed } from './components/reports/ReportFeed'
import { SubmitReportForm } from './features/report-submission/SubmitReportForm'
import { messageOf } from './lib/format'
import { STATUS_LABELS } from './lib/labels'
import type { ReportDetail, ReportSummary, ReviewStatus } from './types/report'

function toSummary(report: ReportDetail): ReportSummary {
  return {
    id: report.id,
    description: report.description,
    location_label: report.location_label,
    latitude: report.latitude,
    longitude: report.longitude,
    source_type: report.source_type,
    source_reference: report.source_reference,
    status: report.status,
    review_note: report.review_note,
    created_at: report.created_at,
    updated_at: report.updated_at,
    freshness: report.freshness,
    category: report.category,
    category_score: report.category_score,
  }
}

export default function App() {
  const [reports, setReports] = useState<ReportSummary[] | null>(null)
  const [listError, setListError] = useState<string | null>(null)

  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [detail, setDetail] = useState<ReportDetail | null>(null)
  const [detailLoading, setDetailLoading] = useState(false)
  const [detailError, setDetailError] = useState<string | null>(null)
  const [actionBusy, setActionBusy] = useState(false)

  const loadReports = useCallback(async () => {
    setListError(null)
    try {
      setReports(await api.listReports())
    } catch (err) {
      setListError(messageOf(err))
    }
  }, [])

  useEffect(() => {
    void loadReports()
  }, [loadReports])

  const openReport = useCallback(async (id: string) => {
    setSelectedId(id)
    setDetail(null)
    setDetailError(null)
    setDetailLoading(true)
    try {
      setDetail(await api.getReport(id))
    } catch (err) {
      setDetailError(messageOf(err))
    } finally {
      setDetailLoading(false)
    }
  }, [])

  const closePanel = useCallback(() => {
    setSelectedId(null)
    setDetail(null)
    setDetailError(null)
  }, [])

  useEffect(() => {
    if (!selectedId) return
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') closePanel()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [selectedId, closePanel])

  const applyUpdate = useCallback((updated: ReportDetail) => {
    setDetail(updated)
    setSelectedId(updated.id)
    const summary = toSummary(updated)
    setReports((previous) => {
      if (previous === null) return [summary]
      const exists = previous.some((item) => item.id === updated.id)
      return exists ? previous.map((item) => (item.id === updated.id ? summary : item)) : [summary, ...previous]
    })
  }, [])

  const runAction = useCallback(
    async (action: () => Promise<ReportDetail>, successMessage: string) => {
      setActionBusy(true)
      try {
        applyUpdate(await action())
        toast.success(successMessage)
      } catch (err) {
        toast.error(messageOf(err))
      } finally {
        setActionBusy(false)
      }
    },
    [applyUpdate],
  )

  function handleCreated(created: ReportDetail) {
    applyUpdate(created)
    toast.success('Report saved as Unverified. Any AI result is a prediction, not a verified fact.')
  }

  function handleClassify() {
    if (!detail) return
    const id = detail.id
    void runAction(() => api.classifyReport(id), 'Classification finished. Shown as a prediction.')
  }

  function handleRefreshWeather() {
    if (!detail) return
    const id = detail.id
    void runAction(() => api.refreshWeather(id), 'Weather updated. It is context, not proof.')
  }

  function handleStatusChange(status: ReviewStatus, note?: string) {
    if (!detail) return
    const id = detail.id
    void runAction(() => api.updateStatus(id, status, note), `Status set to ${STATUS_LABELS[status]}.`)
  }

  return (
    <div className="min-h-dvh">
      <Header />
      <PrototypeBanner />

      <main className="mx-auto grid max-w-6xl gap-6 px-4 pb-16 pt-6 lg:grid-cols-[minmax(0,22rem)_minmax(0,1fr)] lg:px-6">
        <aside>
          <SubmitReportForm onCreated={handleCreated} />
        </aside>

        <section aria-labelledby="feed-heading" className="min-w-0">
          <div className="mb-3 flex items-end justify-between gap-3">
            <div>
              <h2 id="feed-heading" className="text-base font-semibold text-ink">
                Recent reports
              </h2>
              <p className="text-xs text-muted">Newest first. Tap a report to see its evidence.</p>
            </div>
            <button
              type="button"
              onClick={() => void loadReports()}
              className="rounded-xl border border-border px-3 py-1.5 text-xs text-muted hover:text-ink"
            >
              Refresh
            </button>
          </div>
          <ReportFeed
            reports={reports}
            error={listError}
            selectedId={selectedId}
            onOpen={(id) => void openReport(id)}
            onRetry={() => void loadReports()}
          />
        </section>
      </main>

      {selectedId && (
        <EvidencePanel
          report={detail}
          loading={detailLoading}
          error={detailError}
          busy={actionBusy}
          onClose={closePanel}
          onRetryLoad={() => void openReport(selectedId)}
          onClassify={handleClassify}
          onRefreshWeather={handleRefreshWeather}
          onStatusChange={handleStatusChange}
        />
      )}

      <Toaster
        position="bottom-center"
        toastOptions={{
          style: {
            background: 'var(--color-surface-2)',
            color: 'var(--color-ink)',
            border: '1px solid var(--color-border)',
          },
        }}
      />
    </div>
  )
}
