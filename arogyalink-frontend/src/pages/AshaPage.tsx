import { useEffect, useRef, useState } from 'react'
import { ref, onValue, update } from 'firebase/database'
import { rtdb } from '../lib/firebase'

interface CallRecord {
  case_id: string
  phone: string
  state: string
  lang: string
  created_at: number
  extracted_info?: {
    symptom?: string
    severity?: string
    location?: string
    patient_name?: string
  }
  dispatch?: {
    asha_dispatched?: boolean
    asha_accepted?: boolean
    asha_name?: string
    ambulance_dispatched?: boolean
    facility_name?: string
    eta_minutes?: number
    dispatch_time?: number
  }
  triage_level?: string
  diagnosis?: string
  action_summary?: string
}

function playAlertSound() {
  try {
    const ctx = new AudioContext()
    ;[0, 0.3, 0.6].forEach(t => {
      const osc = ctx.createOscillator()
      const gain = ctx.createGain()
      osc.connect(gain)
      gain.connect(ctx.destination)
      osc.frequency.value = 880
      osc.type = 'sine'
      gain.gain.setValueAtTime(0.4, ctx.currentTime + t)
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + t + 0.25)
      osc.start(ctx.currentTime + t)
      osc.stop(ctx.currentTime + t + 0.25)
    })
  } catch {}
}

const SEVERITY_COLOR: Record<string, string> = {
  emergency: 'bg-red-50 border-red-400',
  urgent: 'bg-orange-50 border-orange-400',
  moderate: 'bg-yellow-50 border-yellow-400',
  stable: 'bg-green-50 border-green-400',
}

const SEVERITY_BADGE: Record<string, string> = {
  emergency: 'bg-red-600 text-white',
  urgent: 'bg-orange-500 text-white',
  moderate: 'bg-yellow-500 text-white',
  stable: 'bg-green-600 text-white',
}

const SEVERITY_LABEL: Record<string, string> = {
  emergency: '🚨 EMERGENCY',
  urgent: '⚠️ URGENT',
  moderate: '🟡 MODERATE',
  stable: '✅ STABLE',
}

function timeAgo(ms: number) {
  const diff = Math.floor((Date.now() - ms) / 1000)
  if (diff < 60) return `${diff}s ago`
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
  return `${Math.floor(diff / 3600)}h ago`
}

function mapsUrl(location: string) {
  return `https://maps.google.com/?q=${encodeURIComponent(location)}`
}

export default function AshaPage() {
  const [cases, setCases] = useState<CallRecord[]>([])
  const [newCaseIds, setNewCaseIds] = useState<Set<string>>(new Set())
  const [accepting, setAccepting] = useState<Set<string>>(new Set())
  const [online, setOnline] = useState(true)
  const knownIds = useRef<Set<string>>(new Set())
  const firstLoad = useRef(true)

  useEffect(() => {
    const callsRef = ref(rtdb, 'calls')
    const unsub = onValue(
      callsRef,
      snapshot => {
        const data = snapshot.val() || {}
        const dispatched: CallRecord[] = Object.values(data).filter(
          (c: any) => c.state === 'dispatched' && c.dispatch?.asha_dispatched === true
        ) as CallRecord[]

        dispatched.sort((a, b) => (b.created_at || 0) - (a.created_at || 0))

        if (!firstLoad.current) {
          const fresh: string[] = []
          dispatched.forEach(c => {
            if (!knownIds.current.has(c.case_id)) {
              fresh.push(c.case_id)
              knownIds.current.add(c.case_id)
            }
          })
          if (fresh.length > 0) {
            playAlertSound()
            setNewCaseIds(prev => {
              const next = new Set(prev)
              fresh.forEach(id => next.add(id))
              return next
            })
            setTimeout(() => {
              setNewCaseIds(prev => {
                const next = new Set(prev)
                fresh.forEach(id => next.delete(id))
                return next
              })
            }, 8000)
          }
        } else {
          dispatched.forEach(c => knownIds.current.add(c.case_id))
          firstLoad.current = false
        }

        setCases(dispatched)
        setOnline(true)
      },
      () => setOnline(false)
    )
    return () => unsub()
  }, [])

  async function handleAccept(caseId: string) {
    setAccepting(prev => new Set([...prev, caseId]))
    try {
      const dispatchRef = ref(rtdb, `calls/${caseId}/dispatch`)
      await update(dispatchRef, { asha_accepted: true })
    } catch {
      setAccepting(prev => {
        const next = new Set(prev)
        next.delete(caseId)
        return next
      })
    }
  }

  const sev = (c: CallRecord) => (c.triage_level || 'moderate').toLowerCase()

  const pending = cases.filter(c => !c.dispatch?.asha_accepted)
  const accepted = cases.filter(c => c.dispatch?.asha_accepted)

  return (
    <div className="min-h-screen bg-stone-50">
      {/* Header */}
      <div className="bg-stone-900 text-white px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-red-500 flex items-center justify-center font-bold text-sm">P</div>
          <div>
            <div className="font-semibold text-sm leading-tight">Priya Devi</div>
            <div className="text-stone-400 text-xs">ASHA Worker · Bangalore Rural</div>
          </div>
        </div>
        <div className="flex items-center gap-2 text-xs">
          <div className={`w-2 h-2 rounded-full ${online ? 'bg-green-400' : 'bg-red-400'}`} />
          <span className="text-stone-300">{online ? 'Live' : 'Reconnecting…'}</span>
        </div>
      </div>

      {/* New case alert banner */}
      {newCaseIds.size > 0 && (
        <div className="bg-red-600 text-white text-center py-2.5 px-4 font-semibold animate-pulse text-sm">
          🚨 NEW EMERGENCY ASSIGNED — Respond immediately
        </div>
      )}

      {/* Stats bar */}
      <div className="bg-white border-b border-stone-200 px-4 py-2 flex gap-4 text-xs">
        <span className="text-stone-500">
          <span className="font-semibold text-red-600">{pending.length}</span> pending
        </span>
        <span className="text-stone-500">
          <span className="font-semibold text-green-600">{accepted.length}</span> accepted
        </span>
        <span className="text-stone-500">
          <span className="font-semibold text-stone-700">{cases.length}</span> total active
        </span>
      </div>

      <div className="max-w-lg mx-auto px-4 py-4 space-y-6">

        {/* Pending section */}
        {pending.length > 0 && (
          <div>
            <div className="text-xs font-semibold text-stone-500 uppercase tracking-wide mb-2">
              Needs Response
            </div>
            <div className="space-y-3">
              {pending.map(c => {
                const s = sev(c)
                const isNew = newCaseIds.has(c.case_id)
                const isAccepting = accepting.has(c.case_id)
                const location = c.extracted_info?.location
                return (
                  <div
                    key={c.case_id}
                    className={`rounded-xl border-2 p-4 ${SEVERITY_COLOR[s] || SEVERITY_COLOR.moderate} ${isNew ? 'ring-4 ring-red-400 ring-offset-2' : ''} transition-all`}
                  >
                    {/* Top row */}
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${SEVERITY_BADGE[s] || SEVERITY_BADGE.moderate}`}>
                          {SEVERITY_LABEL[s] || '⚠️ URGENT'}
                        </span>
                        {isNew && (
                          <span className="bg-red-600 text-white text-xs px-2 py-0.5 rounded-full animate-bounce">
                            NEW
                          </span>
                        )}
                      </div>
                      <span className="text-xs text-stone-500 shrink-0 ml-2">{timeAgo(c.created_at)}</span>
                    </div>

                    {/* Details */}
                    <div className="space-y-1 text-sm text-stone-800 mb-3">
                      {c.extracted_info?.patient_name && (
                        <div><span className="font-medium">Patient:</span> {c.extracted_info.patient_name}</div>
                      )}
                      <div>
                        <span className="font-medium">Complaint:</span>{' '}
                        {c.diagnosis || c.extracted_info?.symptom || 'Processing…'}
                      </div>
                      {c.extracted_info?.severity && (
                        <div><span className="font-medium">Condition:</span> {c.extracted_info.severity}</div>
                      )}
                      <div>
                        <span className="font-medium">📍 Location:</span>{' '}
                        {location || 'Unknown'}
                      </div>
                      {c.dispatch?.ambulance_dispatched && c.dispatch.facility_name && (
                        <div className="text-xs text-stone-600">
                          🚑 Ambulance from {c.dispatch.facility_name}
                          {c.dispatch.eta_minutes ? ` · ETA ${c.dispatch.eta_minutes} min` : ''}
                        </div>
                      )}
                    </div>

                    {/* Action buttons */}
                    <div className="flex gap-2 flex-wrap">
                      <button
                        onClick={() => handleAccept(c.case_id)}
                        disabled={isAccepting}
                        className="flex-1 min-w-0 bg-stone-900 text-white text-xs font-semibold py-2 px-3 rounded-lg disabled:opacity-60 active:scale-95 transition-transform"
                      >
                        {isAccepting ? '⏳ Accepting…' : '✅ On My Way'}
                      </button>
                      {location && (
                        <a
                          href={mapsUrl(location)}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex-1 min-w-0 bg-blue-600 text-white text-xs font-semibold py-2 px-3 rounded-lg text-center active:scale-95 transition-transform"
                        >
                          🗺️ Navigate
                        </a>
                      )}
                      <a
                        href={`tel:${c.phone}`}
                        className="bg-green-600 text-white text-xs font-semibold py-2 px-3 rounded-lg active:scale-95 transition-transform"
                      >
                        📞 Call
                      </a>
                    </div>

                    <div className="text-xs text-stone-400 mt-2">Case {c.case_id}</div>
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* Accepted section */}
        {accepted.length > 0 && (
          <div>
            <div className="text-xs font-semibold text-stone-500 uppercase tracking-wide mb-2">
              In Progress
            </div>
            <div className="space-y-3">
              {accepted.map(c => {
                const s = sev(c)
                const location = c.extracted_info?.location
                return (
                  <div
                    key={c.case_id}
                    className="rounded-xl border-2 border-stone-300 bg-white p-4 opacity-80"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${SEVERITY_BADGE[s] || SEVERITY_BADGE.moderate}`}>
                          {SEVERITY_LABEL[s] || '⚠️ URGENT'}
                        </span>
                        <span className="text-xs bg-green-100 text-green-700 font-semibold px-2 py-0.5 rounded-full">
                          ✓ Accepted
                        </span>
                      </div>
                      <span className="text-xs text-stone-400">{timeAgo(c.created_at)}</span>
                    </div>

                    <div className="space-y-1 text-sm text-stone-700 mb-3">
                      {c.extracted_info?.patient_name && (
                        <div><span className="font-medium">Patient:</span> {c.extracted_info.patient_name}</div>
                      )}
                      <div>
                        <span className="font-medium">Complaint:</span>{' '}
                        {c.diagnosis || c.extracted_info?.symptom || 'Processing…'}
                      </div>
                      <div>
                        <span className="font-medium">📍</span>{' '}
                        {location || 'Unknown'}
                      </div>
                    </div>

                    <div className="flex gap-2">
                      {location && (
                        <a
                          href={mapsUrl(location)}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex-1 bg-blue-600 text-white text-xs font-semibold py-2 px-3 rounded-lg text-center"
                        >
                          🗺️ Navigate
                        </a>
                      )}
                      <a
                        href={`tel:${c.phone}`}
                        className="bg-green-600 text-white text-xs font-semibold py-2 px-3 rounded-lg"
                      >
                        📞 Call
                      </a>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* Empty state */}
        {cases.length === 0 && (
          <div className="text-center py-24">
            <div className="text-5xl mb-3">✅</div>
            <div className="text-stone-600 font-medium text-sm">No active emergencies</div>
            <div className="text-stone-400 text-xs mt-1">You'll be notified when a case is assigned</div>
          </div>
        )}

      </div>
    </div>
  )
}
