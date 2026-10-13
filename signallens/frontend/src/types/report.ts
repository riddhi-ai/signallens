// Mirrors the backend Pydantic schemas. Keep the two in sync when either changes.

export type ReviewStatus = 'unverified' | 'under_review' | 'confirmed' | 'disputed' | 'resolved'
export type SourceType = 'community' | 'official' | 'demo'
export type PredictionStatus = 'success' | 'unavailable' | 'error'

export interface Prediction {
  id: string
  task: 'text_classification' | 'image_classification'
  model_id: string
  label: string | null
  score: number | null
  status: PredictionStatus
  message: string | null
  created_at: string
  is_verified: false
}

export interface WeatherSummary {
  temperature_c: number | null
  precipitation_mm: number | null
  weather_code: number | null
  wind_speed_kmh: number | null
}

export interface WeatherContext {
  status: 'success' | 'unavailable'
  provider: string
  latitude: number
  longitude: number
  observed_at: string | null
  retrieved_at: string | null
  summary: WeatherSummary | null
  message: string | null
  note: string
}

export interface EvidenceCheck {
  name: string
  result: string
  detail: string
}

export interface Evidence {
  age_minutes: number
  freshness: 'recent' | 'stale'
  indicators: string[]
  checks: EvidenceCheck[]
}

export interface ReportSummary {
  id: string
  description: string
  location_label: string
  latitude: number
  longitude: number
  source_type: SourceType
  source_reference: string | null
  status: ReviewStatus
  review_note: string | null
  created_at: string
  updated_at: string
  freshness: 'recent' | 'stale'
  category: string | null
  category_score: number | null
}

export interface ReportDetail extends ReportSummary {
  predictions: Prediction[]
  weather: WeatherContext | null
  evidence: Evidence
}

export interface NewReport {
  description: string
  latitude: number
  longitude: number
  location_label: string
}
