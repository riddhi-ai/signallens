import type { ReactNode } from 'react'

export type SectionTone = 'prediction' | 'context' | 'provenance' | 'review'

const TONE: Record<SectionTone, { kicker: string; bar: string }> = {
  prediction: { kicker: 'text-amber', bar: 'border-l-amber' },
  context: { kicker: 'text-cyan', bar: 'border-l-cyan' },
  provenance: { kicker: 'text-muted', bar: 'border-l-border' },
  review: { kicker: 'text-ok', bar: 'border-l-ok' },
}

interface SectionProps {
  kicker: string
  title: string
  note?: string
  tone: SectionTone
  children: ReactNode
}

/** Each part of the evidence panel is its own section, so prediction, context, provenance and review never blur together. */
export function Section({ kicker, title, note, tone, children }: SectionProps) {
  const style = TONE[tone]
  return (
    <section className={`rounded-2xl border border-border border-l-4 bg-surface p-5 ${style.bar}`}>
      <p className={`text-[11px] font-semibold uppercase tracking-[0.14em] ${style.kicker}`}>{kicker}</p>
      <h3 className="mt-1 text-base font-semibold text-ink">{title}</h3>
      {note && <p className="mt-1 text-xs leading-relaxed text-muted">{note}</p>}
      <div className="mt-4 space-y-4">{children}</div>
    </section>
  )
}
