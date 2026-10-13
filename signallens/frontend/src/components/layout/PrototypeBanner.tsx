import { Info } from 'lucide-react'

export function PrototypeBanner() {
  return (
    <div className="border-b border-amber/20 bg-amber/5">
      <p className="mx-auto flex max-w-6xl items-start gap-2 px-4 py-2.5 text-xs leading-relaxed text-ink/90 lg:px-6">
        <Info aria-hidden className="mt-0.5 shrink-0 text-amber" size={14} />
        <span>
          <strong className="font-semibold text-amber">Prototype, not an official alert system.</strong>{' '}
          AI outputs are predictions, not verified facts. Weather is context, not proof. Only a reviewer's explicit action
          changes a report's status.
        </span>
      </p>
    </div>
  )
}
