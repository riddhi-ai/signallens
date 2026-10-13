import { Radar } from 'lucide-react'

export function Header() {
  return (
    <header className="border-b border-border/60 bg-canvas/80 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-4 lg:px-6">
        <div className="flex items-center gap-3">
          <div className="grid size-10 place-items-center rounded-xl border border-cyan/30 bg-cyan/10">
            <Radar aria-hidden className="text-cyan" size={20} />
          </div>
          <div>
            <h1 className="text-lg font-semibold tracking-tight text-ink">SignalLens</h1>
            <p className="text-xs text-muted">Evidence-backed local disruption intelligence</p>
          </div>
        </div>
        <span className="hidden rounded-full border border-amber/40 bg-amber/10 px-3 py-1 text-xs font-medium text-amber sm:inline-block">
          Prototype
        </span>
      </div>
    </header>
  )
}
