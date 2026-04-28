import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { ref, onValue } from 'firebase/database'
import { ChevronLeft, Phone, User, MapPin, AlertCircle, MessageSquare } from 'lucide-react'
import { rtdb } from '../lib/firebase'
import type { Case } from '../lib/types'
import AgentTimeline from '../components/AgentTimeline'
import Badge from '../components/ui/Badge'

const langLabel: Record<string, string> = {
  'en-IN': 'English', 'hi-IN': 'Hindi', 'kn-IN': 'Kannada', 'te-IN': 'Telugu',
}

export default function CaseDetailPage() {
  const { id } = useParams<{ id: string }>()
  const nav = useNavigate()
  const [c, setCase] = useState<Case | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!id) return
    const caseRef = ref(rtdb, `calls/${id}`)
    const unsub = onValue(caseRef, snap => {
      if (snap.exists()) setCase(snap.val() as Case)
      setLoading(false)
    })
    return () => unsub()
  }, [id])

  if (loading) return (
    <div className="p-7 max-w-4xl mx-auto space-y-4">
      {[...Array(3)].map((_, i) => <div key={i} className="bg-white border border-stone-200 rounded-2xl animate-pulse h-24" />)}
    </div>
  )

  if (!c) return (
    <div className="p-7 max-w-4xl mx-auto text-center py-20">
      <AlertCircle size={36} className="text-stone-300 mx-auto mb-3" />
      <p className="text-stone-600 font-medium">Case not found</p>
      <Link to="/admin/cases" className="mt-3 inline-block text-stone-500 text-sm hover:text-stone-900 transition-colors">← Back to cases</Link>
    </div>
  )

  const ext = c.extracted_info ?? {}

  return (
    <div className="p-7 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-3 mb-7">
        <button onClick={() => nav(-1)} className="size-8 rounded-xl text-stone-500 hover:bg-stone-100 flex items-center justify-center transition-colors">
          <ChevronLeft size={18} />
        </button>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h1 className="font-serif text-xl font-semibold text-stone-900 truncate">{c.family_name ?? c.phone}</h1>
            <Badge color={c.state === 'processing' ? 'yellow' : 'green'} dot>{c.state}</Badge>
          </div>
          <p className="text-stone-500 text-xs mt-0.5">
            {new Date(c.created_at).toLocaleString()} · {langLabel[c.lang] ?? c.lang} · {c.source}
          </p>
        </div>
      </div>

      <span className="divider-full block mb-6" />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Left */}
        <div className="lg:col-span-1 space-y-4">
          {/* Extracted info */}
          <div className="bg-white border border-stone-200 rounded-2xl p-5">
            <p className="text-[10px] font-semibold text-stone-400 uppercase tracking-widest mb-4">Extracted Info</p>
            <div className="space-y-3">
              {[
                { label: 'Patient',  icon: <User size={11} />,        value: ext.patient_profile ?? ext.patient_name },
                { label: 'Symptom',  icon: <AlertCircle size={11} />, value: ext.symptom },
                { label: 'Severity', icon: <AlertCircle size={11} />, value: ext.severity },
                { label: 'Location', icon: <MapPin size={11} />,      value: ext.location },
                { label: 'Phone',    icon: <Phone size={11} />,       value: c.phone },
              ].map(({ label, icon, value }) => value && (
                <div key={label}>
                  <p className="text-[10px] text-stone-400 uppercase tracking-wide flex items-center gap-1 mb-0.5">
                    {icon} {label}
                  </p>
                  <p className="text-sm text-stone-700">{value}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Agent pipeline */}
          <div className="bg-white border border-stone-200 rounded-2xl p-5">
            <p className="text-[10px] font-semibold text-stone-400 uppercase tracking-widest mb-4">Agent Pipeline</p>
            <AgentTimeline statuses={c.agent_statuses} />
          </div>

          {/* Triage result */}
          {c.triage_result && (
            <div className="bg-white border border-stone-200 rounded-2xl p-5">
              <p className="text-[10px] font-semibold text-stone-400 uppercase tracking-widest mb-4">Triage Result</p>
              <pre className="text-xs text-stone-600 whitespace-pre-wrap font-mono">
                {JSON.stringify(c.triage_result, null, 2)}
              </pre>
            </div>
          )}
        </div>

        {/* Right: transcript */}
        <div className="lg:col-span-2">
          <div className="bg-white border border-stone-200 rounded-2xl p-5 h-full">
            <p className="text-[10px] font-semibold text-stone-400 uppercase tracking-widest mb-5 flex items-center gap-1.5">
              <MessageSquare size={11} /> Conversation Transcript
            </p>

            {(!c.conversation_history || c.conversation_history.length === 0) ? (
              <p className="text-stone-500 text-sm">No conversation recorded.</p>
            ) : (
              <div className="space-y-3">
                {c.conversation_history.map((msg, i) => (
                  <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-sm ${
                      msg.role === 'user'
                        ? 'bg-stone-900 text-white rounded-br-sm'
                        : 'bg-stone-100 text-stone-800 rounded-bl-sm'
                    }`}>
                      <p className={`text-[10px] font-semibold mb-1 ${msg.role === 'user' ? 'text-stone-400' : 'text-stone-500'}`}>
                        {msg.role === 'user' ? 'Caller' : 'ArogyaLink'}
                      </p>
                      {msg.content}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
