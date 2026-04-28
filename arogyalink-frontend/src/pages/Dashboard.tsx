import { useEffect, useState } from 'react'
import { ref, onValue } from 'firebase/database'
import { Phone, Users, Activity, AlertTriangle } from 'lucide-react'
import { Link } from 'react-router-dom'
import { rtdb } from '../lib/firebase'
import { getDashboardStats, listCases } from '../lib/api'
import type { Case, DashboardStats } from '../lib/types'
import StatCard from '../components/StatCard'
import LiveCallCard from '../components/LiveCallCard'
import Badge from '../components/ui/Badge'

function timeAgo(ms: number) {
  const s = Math.floor((Date.now() - ms) / 1000)
  if (s < 60) return `${s}s ago`
  const m = Math.floor(s / 60)
  if (m < 60) return `${m}m ago`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}h ago`
  return new Date(ms).toLocaleDateString()
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats>({ total_cases: 0, today_cases: 0, active_calls: 0 })
  const [liveCalls, setLiveCalls] = useState<Case[]>([])
  const [recentCases, setRecentCases] = useState<Case[]>([])

  useEffect(() => {
    const callsRef = ref(rtdb, 'calls')
    const unsub = onValue(callsRef, (snap) => {
      if (!snap.exists()) { setLiveCalls([]); return }
      const all = Object.values(snap.val()) as Case[]
      all.sort((a, b) => b.created_at - a.created_at)
      setLiveCalls(all.filter(c => c.state === 'processing'))
    })
    return () => unsub()
  }, [])

  useEffect(() => {
    getDashboardStats().then(setStats).catch(console.error)
    listCases(10).then(setRecentCases).catch(console.error)
  }, [])

  return (
    <div className="p-7 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <p className="text-xs font-semibold text-stone-400 uppercase tracking-widest mb-1">Overview</p>
        <h1 className="font-serif text-3xl font-semibold text-stone-900">Dashboard</h1>
        <span className="divider-full mt-4 block" />
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard label="Active Calls"        value={liveCalls.length}   sub="right now"      accent="red"   icon={<AlertTriangle size={16} />} />
        <StatCard label="Cases Today"         value={stats.today_cases}  sub="last 24 hours"  accent="amber" icon={<Phone size={16} />} />
        <StatCard label="Total Cases"         value={stats.total_cases}                        accent="blue"  icon={<Activity size={16} />} />
        <StatCard label="Families Registered" value="—"                  sub="in database"    accent="green" icon={<Users size={16} />} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Live calls */}
        <section>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-semibold text-stone-800 flex items-center gap-2">
              <span className="size-2 rounded-full bg-emergency animate-pulse" />
              Live Calls
            </h2>
            <span className="text-xs text-stone-400">{liveCalls.length} active</span>
          </div>
          {liveCalls.length === 0 ? (
            <div className="bg-white border border-stone-200 rounded-2xl p-8 text-center">
              <Phone size={28} className="text-stone-300 mx-auto mb-2" />
              <p className="text-stone-500 text-sm">No active calls</p>
            </div>
          ) : (
            <div className="space-y-3">
              {liveCalls.map(c => <LiveCallCard key={c.case_id} c={c} />)}
            </div>
          )}
        </section>

        {/* Recent cases */}
        <section>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-semibold text-stone-800">Recent Cases</h2>
            <Link to="/admin/cases" className="text-xs text-stone-500 hover:text-stone-900 transition-colors">View all →</Link>
          </div>
          <div className="space-y-1.5">
            {recentCases.map(c => (
              <Link
                key={c.case_id}
                to={`/admin/cases/${c.case_id}`}
                className="flex items-center justify-between bg-white border border-stone-200 rounded-xl px-4 py-3 hover:border-stone-300 transition-colors group"
              >
                <div className="min-w-0 flex items-center gap-3">
                  <span className={`size-2 rounded-full shrink-0 ${c.state === 'processing' ? 'bg-emergency animate-pulse' : 'bg-stone-300'}`} />
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-stone-800 truncate">{c.family_name ?? c.phone}</p>
                    <p className="text-xs text-stone-500 truncate">{c.extracted_info?.symptom ?? 'No symptom recorded'}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2 shrink-0 ml-3">
                  <Badge color={c.state === 'processing' ? 'yellow' : 'green'}>{c.state}</Badge>
                  <span className="text-xs text-stone-400">{timeAgo(c.created_at)}</span>
                </div>
              </Link>
            ))}
            {recentCases.length === 0 && (
              <div className="bg-white border border-stone-200 rounded-2xl p-8 text-center">
                <p className="text-stone-500 text-sm">No cases yet</p>
              </div>
            )}
          </div>
        </section>
      </div>
    </div>
  )
}
