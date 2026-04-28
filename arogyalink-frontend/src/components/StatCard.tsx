interface StatCardProps {
  label: string
  value: string | number
  sub?: string
  accent?: 'blue' | 'red' | 'green' | 'amber'
  icon: React.ReactNode
}

const accents = {
  blue:  'bg-stone-100 text-stone-700',
  red:   'bg-red-50 text-emergency',
  green: 'bg-stone-100 text-stone-700',
  amber: 'bg-amber-50 text-amber-700',
}

export default function StatCard({ label, value, sub, accent = 'blue', icon }: StatCardProps) {
  return (
    <div className="bg-white rounded-2xl border border-stone-200 p-5 flex items-start gap-4">
      <div className={`size-9 rounded-xl flex items-center justify-center shrink-0 ${accents[accent]}`}>
        {icon}
      </div>
      <div>
        <p className="text-xs text-stone-500 font-medium">{label}</p>
        <p className="font-serif text-2xl font-semibold text-stone-900 mt-0.5 tracking-tight">{value}</p>
        {sub && <p className="text-[11px] text-stone-400 mt-0.5">{sub}</p>}
      </div>
    </div>
  )
}
