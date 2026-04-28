interface DividerProps { label?: string; className?: string }

export default function Divider({ label, className = '' }: DividerProps) {
  if (label) return (
    <div className={`flex items-center gap-3 ${className}`}>
      <span className="flex-1 h-[1.5px] bg-stone-200 dark:bg-stone-800" />
      <span className="text-[11px] text-stone-400 font-medium uppercase tracking-widest">{label}</span>
      <span className="flex-1 h-[1.5px] bg-stone-200 dark:bg-stone-800" />
    </div>
  )
  return <span className={`block h-[1.5px] bg-stone-200 dark:bg-stone-800 ${className}`} />
}

export function DividerShort({ className = '' }: { className?: string }) {
  return <span className={`block w-[72px] h-[1.5px] bg-stone-900/10 dark:bg-white/10 ${className}`} />
}
