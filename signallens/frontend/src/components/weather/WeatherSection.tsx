import { Loader2, RotateCw } from 'lucide-react'
import { formatMeasure, formatUtc } from '../../lib/format'
import { describeWeatherCode } from '../../lib/labels'
import type { WeatherContext } from '../../types/report'
import { Section } from '../common/Section'

interface WeatherSectionProps {
  weather: WeatherContext | null
  busy: boolean
  onRefresh: () => void
}

export function WeatherSection({ weather, busy, onRefresh }: WeatherSectionProps) {
  return (
    <Section
      kicker="Context"
      title="Weather around the report"
      note="Current conditions from Open-Meteo. Weather is context only. It never proves that an incident happened."
      tone="context"
    >
      {weather === null && <p className="text-sm text-muted">Weather has not been retrieved for this report yet.</p>}

      {weather?.status === 'unavailable' && (
        <p role="status" className="text-sm text-amber">
          Weather is unavailable. <span className="text-muted">{weather.message ?? 'Try again shortly.'}</span>
        </p>
      )}

      {weather?.status === 'success' && weather.summary && (
        <>
          <dl className="grid grid-cols-2 gap-3">
            <Tile label="Temperature" value={formatMeasure(weather.summary.temperature_c, '°C')} />
            <Tile label="Precipitation" value={formatMeasure(weather.summary.precipitation_mm, 'mm')} />
            <Tile label="Wind" value={formatMeasure(weather.summary.wind_speed_kmh, 'km/h')} />
            <Tile label="Conditions" value={describeWeatherCode(weather.summary.weather_code)} />
          </dl>
          <p className="text-xs leading-relaxed text-muted">
            Observed {formatUtc(weather.observed_at)} · Retrieved {formatUtc(weather.retrieved_at)} · {weather.provider}
          </p>
        </>
      )}

      <button
        type="button"
        onClick={onRefresh}
        disabled={busy}
        className="inline-flex items-center gap-2 rounded-xl border border-cyan/40 px-3 py-2 text-sm font-medium text-cyan hover:bg-cyan/10 disabled:opacity-60"
      >
        {busy ? <Loader2 aria-hidden size={14} className="animate-spin" /> : <RotateCw aria-hidden size={14} />}
        {weather ? 'Refresh weather' : 'Get weather'}
      </button>
    </Section>
  )
}

function Tile({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-border bg-canvas/50 p-3">
      <dt className="text-[11px] uppercase tracking-wide text-muted">{label}</dt>
      <dd className="mt-1 text-sm font-medium text-ink">{value}</dd>
    </div>
  )
}
