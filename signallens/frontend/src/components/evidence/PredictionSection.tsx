import { Loader2, RotateCw } from 'lucide-react'
import { formatUtc } from '../../lib/format'
import { CATEGORY_LABELS } from '../../lib/labels'
import type { Prediction } from '../../types/report'
import { Section } from '../common/Section'
import { ScoreBar } from './ScoreBar'

interface PredictionSectionProps {
  predictions: Prediction[]
  busy: boolean
  onClassify: () => void
}

export function PredictionSection({ predictions, busy, onClassify }: PredictionSectionProps) {
  const hasSuccess = predictions.some((prediction) => prediction.status === 'success')
  return (
    <Section
      kicker="AI prediction"
      title="What the model suggests"
      note="These are model predictions, not verified facts. A high score does not change the report's status."
      tone="prediction"
    >
      {predictions.length === 0 && (
        <p className="text-sm text-muted">No model result yet. Run classification to get a prediction.</p>
      )}
      {predictions.map((prediction) => (
        <PredictionRow key={prediction.id} prediction={prediction} />
      ))}
      <button
        type="button"
        onClick={onClassify}
        disabled={busy}
        className="inline-flex items-center gap-2 rounded-xl border border-amber/40 px-3 py-2 text-sm font-medium text-amber hover:bg-amber/10 disabled:opacity-60"
      >
        {busy ? <Loader2 aria-hidden size={14} className="animate-spin" /> : <RotateCw aria-hidden size={14} />}
        {hasSuccess ? 'Run classification again' : 'Run classification'}
      </button>
    </Section>
  )
}

function PredictionRow({ prediction }: { prediction: Prediction }) {
  const label = prediction.label ? (CATEGORY_LABELS[prediction.label] ?? prediction.label) : null
  const succeeded = prediction.status === 'success' && label !== null && prediction.score !== null

  return (
    <div className="rounded-xl border border-border bg-canvas/50 p-3">
      <div className="flex flex-wrap items-center justify-between gap-2 text-xs text-muted">
        <span className="font-mono">{prediction.model_id}</span>
        <span>{formatUtc(prediction.created_at)}</span>
      </div>
      {succeeded ? (
        <div className="mt-3 space-y-3">
          <p className="text-sm text-ink">
            Predicted category: <strong className="font-semibold">{label}</strong>
          </p>
          <ScoreBar value={prediction.score ?? 0} />
        </div>
      ) : (
        <p role="status" className="mt-3 text-sm text-amber">
          {prediction.status === 'unavailable' ? 'Model unavailable.' : 'The model call failed.'}{' '}
          <span className="text-muted">{prediction.message ?? 'No further detail was returned.'}</span>
        </p>
      )}
    </div>
  )
}
