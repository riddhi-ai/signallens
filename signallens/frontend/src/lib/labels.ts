import type { ReviewStatus, SourceType } from '../types/report'

export const CATEGORY_LABELS: Record<string, string> = {
  flooding: 'Flooding or waterlogging',
  road_closure: 'Road closure',
  severe_weather: 'Severe weather',
  infrastructure: 'Infrastructure damage',
  traffic: 'Traffic disruption',
  unclear: 'Unclear or unrelated',
}

export const STATUS_LABELS: Record<ReviewStatus, string> = {
  unverified: 'Unverified',
  under_review: 'Under review',
  confirmed: 'Confirmed',
  disputed: 'Disputed',
  resolved: 'Resolved',
}

export const SOURCE_LABELS: Record<SourceType, string> = {
  community: 'Community report',
  official: 'Official source',
  demo: 'Sample data',
}

export const CHECK_NAME_LABELS: Record<string, string> = {
  freshness: 'Freshness',
  source: 'Source',
  model_agreement: 'Model agreement',
  weather_context: 'Weather context',
  cross_modal: 'Image vs text',
}

export const CHECK_RESULT_LABELS: Record<string, string> = {
  recent: 'Recent',
  stale: 'Stale',
  community: 'Community report',
  official: 'Official source',
  demo: 'Sample data',
  not_assessed: 'Not assessed',
  single_model: 'One model only',
  disagreement: 'Models disagree',
  consistent: 'Consistent with context',
  not_consistent: 'Not consistent with context',
  unavailable: 'Unavailable',
  not_retrieved: 'Not retrieved',
}

const WMO_LABELS: Record<number, string> = {
  0: 'Clear sky',
  1: 'Mainly clear',
  2: 'Partly cloudy',
  3: 'Overcast',
  45: 'Fog',
  48: 'Rime fog',
  51: 'Light drizzle',
  53: 'Drizzle',
  55: 'Dense drizzle',
  61: 'Light rain',
  63: 'Rain',
  65: 'Heavy rain',
  71: 'Light snow',
  73: 'Snow',
  75: 'Heavy snow',
  80: 'Rain showers',
  81: 'Rain showers',
  82: 'Violent rain showers',
  95: 'Thunderstorm',
  96: 'Thunderstorm with hail',
  99: 'Thunderstorm with heavy hail',
}

export function describeWeatherCode(code: number | null): string {
  if (code === null) return 'Not reported'
  return WMO_LABELS[code] ?? `Weather code ${code}`
}
