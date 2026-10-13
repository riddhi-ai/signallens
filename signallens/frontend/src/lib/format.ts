/** Parse a backend timestamp. Values without a zone are treated as UTC, not local time. */
export function parseUtc(value: string): Date {
  const hasZone = /(?:[zZ]|[+-]\d{2}:?\d{2})$/.test(value)
  return new Date(hasZone ? value : `${value}Z`)
}

export function timeAgo(value: string, now: number = Date.now()): string {
  const minutes = Math.max(0, Math.round((now - parseUtc(value).getTime()) / 60_000))
  if (minutes < 1) return 'just now'
  if (minutes < 60) return `${minutes} min ago`
  const hours = Math.round(minutes / 60)
  if (hours < 48) return `${hours} h ago`
  return `${Math.round(hours / 24)} d ago`
}

export function formatUtc(value: string | null): string {
  if (!value) return 'Not recorded'
  const date = parseUtc(value)
  if (Number.isNaN(date.getTime())) return value
  return `${date.toLocaleString('en-GB', { timeZone: 'UTC', dateStyle: 'medium', timeStyle: 'short' })} UTC`
}

export function formatMeasure(value: number | null, unit: string): string {
  return value === null ? 'n/a' : `${value.toFixed(1)} ${unit}`
}

export function percent(value: number): string {
  return `${Math.round(Math.min(1, Math.max(0, value)) * 100)}%`
}

export function messageOf(error: unknown): string {
  return error instanceof Error ? error.message : 'Something went wrong. Please try again.'
}
