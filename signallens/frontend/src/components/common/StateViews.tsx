import { AlertTriangle, Inbox, RotateCw } from 'lucide-react'

export function LoadingCards({ count = 3 }: { count?: number }) {
  return (
    <div className="space-y-3" role="status" aria-label="Loading reports">
      {Array.from({ length: count }, (_, index) => (
        <div key={index} className="animate-pulse rounded-2xl border border-border bg-surface p-4">
          <div className="h-5 w-24 rounded-full bg-surface-2" />
          <div className="mt-4 h-3 w-full rounded bg-surface-2" />
          <div className="mt-2 h-3 w-4/5 rounded bg-surface-2" />
          <div className="mt-4 h-3 w-1/2 rounded bg-surface-2" />
        </div>
      ))}
    </div>
  )
}

export function EmptyState({ title, body }: { title: string; body: string }) {
  return (
    <div className="flex flex-col items-center rounded-2xl border border-dashed border-border bg-surface/50 px-6 py-10 text-center">
      <Inbox aria-hidden className="text-muted" size={28} />
      <p className="mt-3 font-medium text-ink">{title}</p>
      <p className="mt-1 max-w-sm text-sm text-muted">{body}</p>
    </div>
  )
}

export function ErrorState({ message, onRetry, retryLabel = 'Try again' }: { message: string; onRetry?: () => void; retryLabel?: string }) {
  return (
    <div role="alert" className="flex flex-col gap-3 rounded-2xl border border-danger/40 bg-danger/10 p-4 sm:flex-row sm:items-center sm:justify-between">
      <div className="flex items-start gap-3">
        <AlertTriangle aria-hidden className="mt-0.5 shrink-0 text-danger" size={18} />
        <p className="text-sm text-ink">{message}</p>
      </div>
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="inline-flex shrink-0 items-center justify-center gap-2 rounded-xl border border-danger/50 px-3 py-2 text-sm font-medium text-danger hover:bg-danger/10"
        >
          <RotateCw aria-hidden size={14} />
          {retryLabel}
        </button>
      )}
    </div>
  )
}
