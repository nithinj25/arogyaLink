import { CheckCircle, Clock, Loader, XCircle } from 'lucide-react'
import type { AgentStatuses, AgentStatus } from '../lib/types'

const AGENTS: { key: keyof AgentStatuses; label: string }[] = [
  { key: 'orchestrator', label: 'Orchestrator' },
  { key: 'triage',       label: 'Triage' },
  { key: 'location',     label: 'Location' },
  { key: 'dispatch',     label: 'Dispatch' },
  { key: 'comms',        label: 'Comms' },
]

function StatusIcon({ status }: { status: AgentStatus }) {
  if (status === 'complete') return <CheckCircle size={15} className="text-green-500" />
  if (status === 'active')   return <Loader size={15} className="text-blue-500 animate-spin" />
  if (status === 'error')    return <XCircle size={15} className="text-red-500" />
  return <Clock size={15} className="text-slate-300" />
}

const pill: Record<AgentStatus, string> = {
  complete: 'bg-green-50 text-green-700 border-green-200',
  active:   'bg-blue-50 text-blue-700 border-blue-200',
  error:    'bg-red-50 text-red-700 border-red-200',
  pending:  'bg-slate-50 text-slate-400 border-slate-200',
}

export default function AgentTimeline({ statuses }: { statuses: AgentStatuses }) {
  return (
    <div className="flex flex-wrap gap-2">
      {AGENTS.map(({ key, label }) => {
        const s = statuses[key] ?? 'pending'
        return (
          <div key={key} className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full border text-xs font-medium ${pill[s]}`}>
            <StatusIcon status={s} />
            {label}
          </div>
        )
      })}
    </div>
  )
}
