import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Phone, Clock, ChevronRight, Search } from 'lucide-react'
import { listCases } from '../lib/api'
import type { Case } from '../lib/types'
import Input from '../components/ui/Input'
import Badge from '../components/ui/Badge'

const langLabel: Record<string, string> = {
  'en-IN': 'EN', 'hi-IN': 'HI', 'kn-IN': 'KN', 'te-IN': 'TE',
}

function timeAgo(ms: number) {
  const s = Math.floor((Date.now() - ms) / 1000)
  if (s < 60) return `${s}s ago`
  const m = Math.floor(s / 60)
  if (m < 60) return `${m}m ago`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}h ago`
  return new Date(ms).toLocaleDateString()
}

export default function CasesPage() {
  const [cases, setCases] = useState<Case[]>([])
  const [filtered, setFiltered] = useState<Case[]>([])
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    listCases(100)
      .then(data => { setCases(data); setFiltered(data) })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (!search) { setFiltered(cases); return }
    const q = search.toLowerCase()
    setFiltered(cases.filter(c =>
      c.phone.includes(q)
      || (c.family_name ?? '').toLowerCase().includes(q)
      || (c.extracted_info?.symptom ?? '').toLowerCase().includes(q)
      || c.case_id.toLowerCase().includes(q)
    ))
  }, [search, cases])

  return (
    <div className="p-7 max-w-4xl mx-auto">
      <div className="mb-8">
        <p className="text-xs font-semibold text-stone-400 uppercase tracking-widest mb-1">History</p>
        <h1 className="font-serif text-3xl font-semibold text-stone-900">Cases</h1>
        <p className="text-stone-500 text-sm mt-1">{cases.length} total cases</p>
      </div>

      <span className="divider-full block mb-6" />

      <div className="mb-6">
        <Input
          leading={<Search size={14} />}
          value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="Search by phone, name, symptom, or case ID…"
        />
      </div>

      {loading ? (
        <div className="space-y-2">
          {[...Array(8)].map((_, i) => (
            <div key={i} className="bg-white border border-stone-200 rounded-2xl h-16 animate-pulse" />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <div className="bg-white border border-stone-200 rounded-2xl p-12 text-center">
          <Phone size={32} className="text-stone-300 mx-auto mb-3" />
          <p className="text-stone-500 text-sm">No cases found</p>
        </div>
      ) : (
        <div className="space-y-1.5">
          {filtered.map(c => (
            <Link
              key={c.case_id}
              to={`/admin/cases/${c.case_id}`}
              className="flex items-center justify-between bg-white border border-stone-200 rounded-2xl px-5 py-3.5 hover:border-stone-300 transition-all group"
            >
              <div className="flex items-center gap-4 min-w-0">
                <span className={`size-2 rounded-full shrink-0 ${c.state === 'processing' ? 'bg-emergency animate-pulse' : 'bg-stone-300'}`} />
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-sm text-stone-800 truncate">{c.family_name ?? c.phone}</span>
                    {c.family_name && <Badge color="stone">Reg.</Badge>}
                    <Badge color="stone">{langLabel[c.lang] ?? c.lang}</Badge>
                  </div>
                  <p className="text-xs text-stone-500 truncate mt-0.5">
                    {c.extracted_info?.symptom ?? 'No symptom recorded'}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3 shrink-0">
                <div className="text-right hidden sm:block">
                  <span className="flex items-center gap-1 text-xs text-stone-400 justify-end">
                    <Clock size={10} /> {timeAgo(c.created_at)}
                  </span>
                  <Badge color={c.state === 'processing' ? 'yellow' : 'green'} className="mt-1">
                    {c.state}
                  </Badge>
                </div>
                <ChevronRight size={15} className="text-stone-300 group-hover:text-stone-600 transition-colors" />
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
