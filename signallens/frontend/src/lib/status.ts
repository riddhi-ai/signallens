import type { ReviewStatus } from '../types/report'

// Mirrors backend/app/services/status.py. The server is the authority; this only drives which buttons appear.
export const ALLOWED_NEXT: Record<ReviewStatus, ReviewStatus[]> = {
  unverified: ['under_review', 'confirmed', 'disputed'],
  under_review: ['unverified', 'confirmed', 'disputed'],
  confirmed: ['under_review', 'disputed', 'resolved'],
  disputed: ['under_review', 'confirmed', 'resolved'],
  resolved: ['under_review'],
}
