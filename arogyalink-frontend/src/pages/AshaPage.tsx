import { useEffect, useRef, useState } from 'react'
import { ref, onValue } from 'firebase/database'
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
    const times = [0, 0.3, 0.6]
    times.forEach(t => {
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
  emergency: 'bg-red-100 border-red-400 text-red-800',
  urgent: 'bg-orange-100 border-orange-400 text-orange-800',
  moderate: 'bg-yellow-100 border-yellow-400 text-yellow-800',
  stable: 'bg-green-100 border-green-400 text-green-800',
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

export default function AshaPage() {
  const [cases, setCases] = useState<CallRecord[]>([])
  const [newCaseIds, setNewCaseIds] = useState<Set<string>>(new Set())
  const [online, setOnline] = useState(true)
  const knownIds = useRef<Set<string>>(new Set())
  const firstLoad = useRef(true)

  useEffect(() => {
    const callsRef = ref(rtdb, 'calls')
    const unsub = onValue(callsRef, snapshot => {
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
    }, () => setOnline(false))

    return () => unsub()
  }, [])

  const severity = (c: CallRecord) =>
    (c.triage_level || 'moderate').toLowerCase()

  return (
    <div className="min-h-screen bg-stone-50">
      {/* Header */}
      <div className="bg-stone-900 text-white px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-red-500 flex items-center justify-center text-lg font-bold">P</div>
          <div>
            <div className="font-semibold text-base leading-tight">Priya Devi</div>
            <div className="text-stone-400 text-xs">ASHA Worker · Bangalore Rural</div>
          </div>
        </div>
        <div className="flex items-center gap-2 text-sm">
          <div className={`w-2 h-2 rounded-full ${online ? 'bg-green-400' : 'bg-red-400'}`} />
          <span className="text-stone-300">{online ? 'Live' : 'Reconnecting…'}</span>
        </div>
      </div>

      {/* Alert banner for new case */}
      {newCaseIds.size > 0 && (
        <div className="bg-red-600 text-white text-center py-3 px-4 font-semibold animate-pulse text-sm">
          🚨 NEW EMERGENCY ASSIGNED — Please respond immediately
        </div>
      )}

      <div className="max-w-lg mx-auto px-4 py-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold text-stone-800 text-base">
            My Assignments
          </h2>
          <span className="text-xs text-stone-500 bg-stone-200 px-2 py-1 rounded-full">
            {cases.length} active
          </span>
        </div>

        {cases.length === 0 ? (
          <div className="text-center py-20">
            <div className="text-4xl mb-3">✅</div>
            <div className="text-stone-500 text-sm">No active emergencies</div>
            <div className="text-stone-400 text-xs mt-1">You'll be notified when a case is assigned</div>
          </div>
        ) : (
          <div className="space-y-3">
            {cases.map(c => {
              const sev = severity(c)
              const colorClass = SEVERITY_COLOR[sev] || SEVERITY_COLOR.moderate
              const isNew = newCaseIds.has(c.case_id)
              return (
                <div
                  key={c.case_id}
                  className={`rounded-xl border-2 p-4 ${colorClass} ${isNew ? 'ring-4 ring-red-400 ring-offset-2' : ''} transition-all`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <span className="font-bold text-sm">
                        {SEVERITY_LABEL[sev] || '⚠️ URGENT'}
                      </span>
                      {isNew && (
                        <span className="ml-2 bg-red-600 text-white text-xs px-2 py-0.5 rounded-full animate-bounce">
                          NEW
                        </span>
                      )}
                    </div>
                    <span className="text-xs opacity-70">
                      {timeAgo(c.created_at)}
                    </span>
                  </div>

                  <div className="space-y-1.5 text-sm">
                    {c.extracted_info?.patient_name && (
                      <div><span className="font-medium">Patient:</span> {c.extracted_info.patient_name}</div>
                    )}
                    <div>
                      <span className="font-medium">Complaint:</span>{' '}
                      {c.diagnosis || c.extracted_info?.symptom || 'Details being processed…'}
                    </div>
                    {c.extracted_info?.severity && (
                      <div><span className="font-medium">Condition:</span> {c.extracted_info.severity}</div>
                    )}
                    <div>
                      <span className="font-medium">📍 Location:</span>{' '}
                      {c.extracted_info?.location || 'Unknown'}
                    </div>
                    {c.dispatch?.ambulance_dispatched && c.dispatch.facility_name && (
                      <div className="text-xs mt-1 opacity-80">
                        🚑 Ambulance from {c.dispatch.facility_name}
                        {c.dispatch.eta_minutes ? ` · ETA ${c.dispatch.eta_minutes} min` : ''}
                      </div>
                    )}
                    <div className="text-xs opacity-70 mt-1">
                      Caller: {c.phone} · Case {c.case_id}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
