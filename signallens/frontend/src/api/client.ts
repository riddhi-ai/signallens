import type { NewReport, ReportDetail, ReportSummary, ReviewStatus } from '../types/report'

const API_BASE_URL =
  (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/$/, '') || 'http://localhost:8000'

// Model calls can take a while (each has a timeout and one retry on the server),
// so slow endpoints get a longer client-side budget.
const TIMEOUT_MS = { default: 12_000, classify: 30_000, create: 45_000 } as const

export class ApiError extends Error {
  readonly status: number | null
  readonly retryable: boolean

  constructor(message: string, status: number | null, retryable: boolean) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.retryable = retryable
  }
}

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PATCH'
  body?: unknown
  timeoutMs?: number
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', body, timeoutMs = TIMEOUT_MS.default } = options
  const controller = new AbortController()
  const timer = window.setTimeout(() => controller.abort(), timeoutMs)
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method,
      headers: {
        Accept: 'application/json',
        ...(body !== undefined ? { 'Content-Type': 'application/json' } : {}),
      },
      body: body !== undefined ? JSON.stringify(body) : undefined,
      signal: controller.signal,
    })
    if (!response.ok) {
      const retryable = response.status === 429 || response.status >= 500
      throw new ApiError(await readErrorMessage(response), response.status, retryable)
    }
    return (await response.json()) as T
  } catch (error) {
    if (error instanceof ApiError) throw error
    const timedOut = error instanceof DOMException && error.name === 'AbortError'
    throw new ApiError(
      timedOut
        ? 'The request took too long. Check your connection and try again.'
        : 'Could not reach the SignalLens API. Is the backend running?',
      null,
      true,
    )
  } finally {
    window.clearTimeout(timer)
  }
}

async function readErrorMessage(response: Response): Promise<string> {
  const fallback = `The request failed (HTTP ${response.status}).`
  try {
    const data: unknown = await response.json()
    if (data && typeof data === 'object' && 'detail' in data) {
      const detail = (data as { detail: unknown }).detail
      if (typeof detail === 'string') return detail
      if (Array.isArray(detail) && detail.length > 0) {
        const first = detail[0] as { msg?: unknown }
        if (typeof first?.msg === 'string') return `Check your input: ${first.msg}.`
      }
    }
  } catch {
    // The body was not JSON; keep the generic message.
  }
  return fallback
}

const path = (id: string, suffix = '') => `/api/reports/${encodeURIComponent(id)}${suffix}`

export const api = {
  listReports: () => request<ReportSummary[]>('/api/reports'),

  getReport: (id: string) => request<ReportDetail>(path(id)),

  createReport: (input: NewReport) =>
    request<ReportDetail>('/api/reports', { method: 'POST', body: input, timeoutMs: TIMEOUT_MS.create }),

  classifyReport: (id: string) =>
    request<ReportDetail>(path(id, '/classify'), { method: 'POST', timeoutMs: TIMEOUT_MS.classify }),

  refreshWeather: (id: string) => request<ReportDetail>(path(id, '/weather'), { method: 'POST' }),

  updateStatus: (id: string, status: ReviewStatus, note?: string) =>
    request<ReportDetail>(path(id, '/status'), {
      method: 'PATCH',
      body: { status, note: note ?? null },
    }),
}
