import { CHECK_NAME_LABELS, CHECK_RESULT_LABELS, SOURCE_LABELS } from '../../lib/labels'
import { formatUtc } from '../../lib/format'
import type { ReportDetail } from '../../types/report'
import { Section } from '../common/Section'

export function ProvenanceSection({ report }: { report: ReportDetail }) {
  const { evidence } = report
  return (
    <Section
      kicker="Provenance"
      title="Source, timing and checks"
      note="Each check is shown on its own. None of them is combined into a single score."
      tone="provenance"
    >
      <dl className="grid grid-cols-1 gap-3 text-sm sm:grid-cols-2">
        <Field label="Source" value={SOURCE_LABELS[report.source_type]} />
        <Field label="Source reference" value={report.source_reference ?? 'None recorded'} />
        <Field label="Submitted" value={formatUtc(report.created_at)} />
        <Field label="Last updated" value={formatUtc(report.updated_at)} />
        <Field label="Coordinates" value={`${report.latitude.toFixed(4)}, ${report.longitude.toFixed(4)}`} />
        <Field
          label="Age"
          value={`${evidence.age_minutes} min · ${CHECK_RESULT_LABELS[evidence.freshness] ?? evidence.freshness}`}
        />
      </dl>

      <ul className="divide-y divide-border/70 rounded-xl border border-border">
        {evidence.checks.map((check) => (
          <li key={check.name} className="p-3 text-sm">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <span className="font-medium text-ink">{CHECK_NAME_LABELS[check.name] ?? check.name}</span>
              <span className="rounded-full bg-surface-2 px-2 py-0.5 text-xs text-muted">
                {CHECK_RESULT_LABELS[check.result] ?? check.result}
              </span>
            </div>
            <p className="mt-1 text-xs leading-relaxed text-muted">{check.detail}</p>
          </li>
        ))}
      </ul>

      {evidence.indicators.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {evidence.indicators.map((indicator) => (
            <span key={indicator} className="rounded-full border border-border px-2.5 py-0.5 font-mono text-[11px] text-muted">
              {indicator}
            </span>
          ))}
        </div>
      )}
    </Section>
  )
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-[11px] uppercase tracking-wide text-muted">{label}</dt>
      <dd className="mt-0.5 text-ink">{value}</dd>
    </div>
  )
}
