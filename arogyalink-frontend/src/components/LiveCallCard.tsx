import { Phone, Clock, User } from 'lucide-react'
import { Link } from 'react-router-dom'
import type { Case } from '../lib/types'
import AgentTimeline from './AgentTimeline'

function elapsed(ms: number) {
  const s = Math.floor((Date.now() - ms) / 1000)
  if (s < 60) return `${s}s ago`
  const m = Math.floor(s / 60)
  if (m < 60) return `${m}m ago`
  return `${Math.floor(m / 60)}h ago`
}

const langLabel: Record<string, string> = {
  'en-IN': 'English', 'hi-IN': 'Hindi', 'kn-IN': 'Kannada', 'te-IN': 'Telugu',
}

export default function LiveCallCard({ c }: { c: Case }) {
  const isActive = c.state === 'processing'
  return (
    <Link
      to={`/admin/cases/${c.case_id}`}
      className="block bg-white border border-stone-200 rounded-2xl p-4 hover:border-stone-300 transition-all"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2.5">
          <div className={`size-8 rounded-xl flex items-center justify-center ${isActive ? 'bg-red-50' : 'bg-stone-100'}`}>
            <Phone size={14} className={isActive ? 'text-emergency' : 'text-stone-400'} />
          </div>
          <div>
            <p className="font-semibold text-sm text-stone-800">{c.family_name ?? c.phone}</p>
            <p className="text-xs text-stone-500">{c.phone}</p>
          </div>
        </div>

        <span className={`inline-flex items-center gap-1.5 text-[11px] font-medium px-2.5 py-1 rounded-full border ${
          isActive ? 'bg-red-50 text-red-700 border-red-200' : 'bg-stone-50 text-stone-500 border-stone-200'
        }`}>
          {isActive && <span className="size-1.5 rounded-full bg-emergency animate-pulse" />}
          {isActive ? 'Live' : c.state}
        </span>
      </div>

      <div className="mt-3 flex items-center gap-4 text-xs text-stone-500">
        <span className="flex items-center gap-1"><Clock size={11} /> {elapsed(c.created_at)}</span>
        <span className="flex items-center gap-1"><User size={11} /> {langLabel[c.lang] ?? c.lang}</span>
        {c.family_name && (
          <span className="px-2 py-0.5 bg-stone-100 text-stone-600 rounded-full text-[10px] font-medium">Registered</span>
        )}
      </div>

      {c.extracted_info?.symptom && (
        <p className="mt-2 text-xs text-stone-600 bg-stone-50 rounded-xl px-3 py-1.5 truncate">
          {c.extracted_info.symptom}
        </p>
      )}

      <div className="mt-3">
        <AgentTimeline statuses={c.agent_statuses} />
      </div>
    </Link>
  )
}
