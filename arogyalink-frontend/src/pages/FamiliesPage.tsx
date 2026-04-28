import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Search, Plus, Phone, MapPin, Users, ChevronRight } from 'lucide-react'
import { listFamilies } from '../lib/api'
import type { Family } from '../lib/types'
import Button from '../components/ui/Button'
import Input from '../components/ui/Input'
import Badge from '../components/ui/Badge'

const langLabel: Record<string, string> = {
  'en-IN': 'EN', 'hi-IN': 'HI', 'kn-IN': 'KN', 'te-IN': 'TE',
}

export default function FamiliesPage() {
  const [families, setFamilies] = useState<Family[]>([])
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = (q?: string) => {
    setLoading(true)
    listFamilies(q)
      .then(setFamilies)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const handleSearch = (e: React.FormEvent) => { e.preventDefault(); load(search || undefined) }

  return (
    <div className="p-7 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-start justify-between mb-8">
        <div>
          <p className="text-xs font-semibold text-stone-400 uppercase tracking-widest mb-1">Registry</p>
          <h1 className="font-serif text-3xl font-semibold text-stone-900">Families</h1>
          <p className="text-stone-500 text-sm mt-1">{families.length} families registered</p>
        </div>
        <Link to="/admin/families/new">
          <Button icon={<Plus size={14} />}>Register Family</Button>
        </Link>
      </div>

      <span className="divider-full block mb-6" />

      {/* Search */}
      <form onSubmit={handleSearch} className="mb-6">
        <Input
          leading={<Search size={14} />}
          trailing={<button type="submit" className="text-xs text-stone-500 hover:text-stone-900 transition-colors px-1">Search</button>}
          value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="Search by name, village, or phone…"
        />
      </form>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-xl px-4 py-3 mb-4">{error}</div>
      )}

      {loading ? (
        <div className="space-y-2">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="bg-white border border-stone-200 rounded-2xl h-20 animate-pulse" />
          ))}
        </div>
      ) : families.length === 0 ? (
        <div className="bg-white border border-stone-200 rounded-2xl p-12 text-center">
          <Users size={32} className="text-stone-300 mx-auto mb-3" />
          <p className="text-stone-700 font-medium text-sm">No families registered yet</p>
          <p className="text-stone-400 text-sm mt-1 mb-5">Register a family to enable personalised emergency calls</p>
          <Link to="/admin/families/new">
            <Button icon={<Plus size={14} />}>Register First Family</Button>
          </Link>
        </div>
      ) : (
        <div className="space-y-1.5">
          {families.map(f => (
            <Link
              key={f.phone}
              to={`/admin/families/${encodeURIComponent(f.phone)}`}
              className="flex items-center justify-between bg-white border border-stone-200 rounded-2xl px-5 py-4 hover:border-stone-300 transition-all group"
            >
              <div className="flex items-center gap-4 min-w-0">
                <div className="size-9 rounded-full bg-stone-100 flex items-center justify-center text-stone-700 font-semibold text-sm shrink-0">
                  {f.primary_name.charAt(0).toUpperCase()}
                </div>
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="font-semibold text-stone-800 text-sm">{f.primary_name}</p>
                    <Badge color="stone">{langLabel[f.language] ?? f.language}</Badge>
                  </div>
                  <div className="flex items-center gap-3 mt-0.5">
                    <span className="flex items-center gap-1 text-xs text-stone-500">
                      <Phone size={10} /> {f.phone}
                    </span>
                    {(f.village || f.district) && (
                      <span className="flex items-center gap-1 text-xs text-stone-500">
                        <MapPin size={10} /> {[f.village, f.district].filter(Boolean).join(', ')}
                      </span>
                    )}
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-4 shrink-0">
                <div className="text-right hidden sm:block">
                  <p className="text-xs text-stone-500">{f.members.length} member{f.members.length !== 1 ? 's' : ''}</p>
                  {f.call_count > 0 && (
                    <p className="text-xs text-stone-400 mt-0.5">{f.call_count} call{f.call_count !== 1 ? 's' : ''}</p>
                  )}
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
