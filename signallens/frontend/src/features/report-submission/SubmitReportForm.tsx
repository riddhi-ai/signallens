import { Loader2, Send } from 'lucide-react'
import { useState, type FormEvent } from 'react'
import { api } from '../../api/client'
import { DEMO_LOCATIONS } from '../../data/locations'
import { messageOf } from '../../lib/format'
import type { ReportDetail } from '../../types/report'

const MIN_LENGTH = 10
const MAX_LENGTH = 500

interface SubmitReportFormProps {
  onCreated: (report: ReportDetail) => void
}

export function SubmitReportForm({ onCreated }: SubmitReportFormProps) {
  const [locationIndex, setLocationIndex] = useState(0)
  const [description, setDescription] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [showErrors, setShowErrors] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const trimmed = description.trim()
  const problem =
    trimmed.length < MIN_LENGTH
      ? `Describe the disruption in at least ${MIN_LENGTH} characters.`
      : trimmed.length > MAX_LENGTH
        ? `Keep it to ${MAX_LENGTH} characters or fewer.`
        : null
  const location = DEMO_LOCATIONS[locationIndex]

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setShowErrors(true)
    if (problem || submitting) return

    setSubmitting(true)
    setError(null)
    try {
      const created = await api.createReport({
        description: trimmed,
        latitude: location.latitude,
        longitude: location.longitude,
        location_label: location.label,
      })
      setDescription('')
      setShowErrors(false)
      onCreated(created)
    } catch (err) {
      // Keep the text so the user can retry without retyping.
      setError(messageOf(err))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} noValidate className="space-y-4 rounded-2xl border border-border bg-surface p-5">
      <div>
        <h2 className="text-base font-semibold text-ink">Report a disruption</h2>
        <p className="mt-1 text-xs leading-relaxed text-muted">
          Describe what you see. Avoid personal details such as names, phone numbers or exact home addresses.
        </p>
      </div>

      <div className="space-y-1.5">
        <label htmlFor="location" className="text-xs font-medium text-muted">
          Area
        </label>
        <select
          id="location"
          value={locationIndex}
          onChange={(event) => setLocationIndex(Number(event.target.value))}
          className="w-full rounded-xl border border-border bg-canvas px-3 py-2.5 text-sm text-ink focus:border-cyan/60 focus:outline-none"
        >
          {DEMO_LOCATIONS.map((option, index) => (
            <option key={option.label} value={index}>
              {option.label}
            </option>
          ))}
        </select>
      </div>

      <div className="space-y-1.5">
        <label htmlFor="description" className="text-xs font-medium text-muted">
          What is happening?
        </label>
        <textarea
          id="description"
          rows={4}
          value={description}
          onChange={(event) => setDescription(event.target.value)}
          aria-invalid={showErrors && problem !== null}
          aria-describedby="description-help"
          placeholder="e.g. Water is collecting near the underpass. Cars are slowing down."
          className="w-full resize-y rounded-xl border border-border bg-canvas px-3 py-2.5 text-sm text-ink placeholder:text-muted/70 focus:border-cyan/60 focus:outline-none"
        />
        <div id="description-help" className="flex justify-between text-xs">
          <span className={showErrors && problem ? 'text-danger' : 'text-muted'}>
            {showErrors && problem ? problem : 'A prediction runs on the server. Your report stays Unverified.'}
          </span>
          <span className={`tabular-nums ${trimmed.length > MAX_LENGTH ? 'text-danger' : 'text-muted'}`}>
            {trimmed.length}/{MAX_LENGTH}
          </span>
        </div>
      </div>

      {error && (
        <p role="alert" className="rounded-xl border border-danger/40 bg-danger/10 px-3 py-2 text-xs text-danger">
          {error} Your text is kept, so you can try again.
        </p>
      )}

      <button
        type="submit"
        disabled={submitting}
        className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-cyan px-4 py-2.5 text-sm font-semibold text-canvas transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {submitting ? <Loader2 aria-hidden size={16} className="animate-spin" /> : <Send aria-hidden size={16} />}
        {submitting ? 'Checking the report…' : 'Submit report'}
      </button>
    </form>
  )
}
