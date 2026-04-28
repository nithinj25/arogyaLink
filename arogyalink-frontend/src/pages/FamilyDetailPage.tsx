import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { ChevronLeft, Phone, MapPin, Trash2, Heart, Droplets, AlertCircle } from 'lucide-react'
import { getFamily, deleteFamily, listCases } from '../lib/api'
import type { Family, Case } from '../lib/types'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'

const langLabel: Record<string, string> = {
  'en-IN': 'English', 'hi-IN': 'Hindi', 'kn-IN': 'Kannada', 'te-IN': 'Telugu',
}

function MemberCard({ m }: { m: Family['members'][0] }) {
  return (
    <div className="bg-stone-50 border border-stone-200 rounded-2xl p-4">
      <div className="flex items-start justify-between gap-3 mb-3">
        <div>
          <p className="font-semibold text-stone-800">{m.name}</p>
          <p className="text-xs text-stone-500 mt-0.5 capitalize">
            {m.relationship} · {m.age} yrs · {m.gender === 'M' ? 'Male' : m.gender === 'F' ? 'Female' : 'Other'}
          </p>
        </div>
        {m.blood_group && (
          <span className="flex items-center gap-1 text-xs font-bold text-red-700 bg-red-50 border border-red-200 px-2 py-0.5 rounded-full">
            <Droplets size={10} /> {m.blood_group}
          </span>
        )}
      </div>
      {m.conditions.length > 0 && (
        <div className="mb-2">
          <p className="text-[10px] font-semibold text-stone-400 uppercase tracking-widest mb-1.5">Conditions</p>
          <div className="flex flex-wrap gap-1">
            {m.conditions.map(c => <Badge key={c} color="yellow">{c}</Badge>)}
          </div>
        </div>
      )}
      {m.allergies.length > 0 && (
        <div>
          <p className="text-[10px] font-semibold text-stone-400 uppercase tracking-widest mb-1.5">Allergies</p>
          <div className="flex flex-wrap gap-1">
            {m.allergies.map(a => <Badge key={a} color="red">{a}</Badge>)}
          </div>
        </div>
      )}
    </div>
  )
}

export default function FamilyDetailPage() {
  const { phone } = useParams<{ phone: string }>()
  const nav = useNavigate()
  const [family, setFamily] = useState<Family | null>(null)
  const [cases, setCases] = useState<Case[]>([])
  const [loading, setLoading] = useState(true)
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    if (!phone) return
    Promise.all([getFamily(decodeURIComponent(phone)), listCases(100)])
      .then(([fam, allCases]) => {
        setFamily(fam)
        setCases(allCases.filter(c => c.phone === fam.phone || c.family_phone === fam.phone))
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [phone])

  const handleDelete = async () => {
    if (!family || !window.confirm(`Delete family profile for ${family.primary_name}?`)) return
    setDeleting(true)
    try {
      await deleteFamily(family.phone)
      nav('/admin/families')
    } catch (e) {
      alert((e as Error).message)
      setDeleting(false)
    }
  }

  if (loading) return (
    <div className="p-7 max-w-4xl mx-auto space-y-4">
      {[...Array(3)].map((_, i) => <div key={i} className="bg-white border border-stone-200 rounded-2xl animate-pulse h-24" />)}
    </div>
  )

  if (!family) return (
    <div className="p-7 max-w-4xl mx-auto text-center py-20">
      <AlertCircle size={36} className="text-stone-300 mx-auto mb-3" />
      <p className="text-stone-600 font-medium">Family not found</p>
      <Link to="/admin/families" className="mt-3 inline-block text-stone-500 text-sm hover:text-stone-900 transition-colors">← Back to families</Link>
    </div>
  )

  return (
    <div className="p-7 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-3 mb-7">
        <button onClick={() => nav(-1)} className="size-8 rounded-xl text-stone-500 hover:bg-stone-100 flex items-center justify-center transition-colors">
          <ChevronLeft size={18} />
        </button>
        <div className="flex-1 min-w-0">
          <h1 className="font-serif text-2xl font-semibold text-stone-900 truncate">{family.primary_name}</h1>
          <p className="text-stone-500 text-sm mt-0.5">{langLabel[family.language]} · {family.phone}</p>
        </div>
        <Button variant="danger" size="sm" icon={<Trash2 size={13} />} loading={deleting} onClick={handleDelete}>
          Delete
        </Button>
      </div>

      <span className="divider-full block mb-6" />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Left */}
        <div className="lg:col-span-1 space-y-4">
          <div className="bg-white border border-stone-200 rounded-2xl p-5">
            <p className="text-[10px] font-semibold text-stone-400 uppercase tracking-widest mb-3">Address</p>
            <div className="flex items-start gap-2 text-sm text-stone-700">
              <MapPin size={14} className="text-stone-400 mt-0.5 shrink-0" />
              <p>{[family.address, family.village, family.district, family.state, family.pin].filter(Boolean).join(', ')}</p>
            </div>
          </div>

          <div className="bg-white border border-stone-200 rounded-2xl p-5">
            <p className="text-[10px] font-semibold text-stone-400 uppercase tracking-widest mb-3">Activity</p>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-stone-500 flex items-center gap-1.5"><Phone size={13} /> Total calls</span>
                <span className="font-semibold text-stone-800">{family.call_count}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-stone-500 flex items-center gap-1.5"><Heart size={13} /> Members</span>
                <span className="font-semibold text-stone-800">{family.members.length}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right */}
        <div className="lg:col-span-2 space-y-6">
          <div>
            <p className="text-xs font-semibold text-stone-400 uppercase tracking-widest mb-3">Family Members</p>
            {family.members.length === 0 ? (
              <p className="text-stone-500 text-sm">No members added yet.</p>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {family.members.map(m => <MemberCard key={m.id} m={m} />)}
              </div>
            )}
          </div>

          <div>
            <p className="text-xs font-semibold text-stone-400 uppercase tracking-widest mb-3">Call History</p>
            {cases.length === 0 ? (
              <p className="text-stone-500 text-sm">No calls recorded yet.</p>
            ) : (
              <div className="space-y-1.5">
                {cases.map(c => (
                  <Link key={c.case_id} to={`/admin/cases/${c.case_id}`}
                    className="flex items-center justify-between bg-white border border-stone-200 rounded-xl px-4 py-3 hover:border-stone-300 transition-colors">
                    <div>
                      <p className="text-sm font-medium text-stone-700">{c.extracted_info?.symptom ?? 'No symptom recorded'}</p>
                      <p className="text-xs text-stone-400 mt-0.5">{new Date(c.created_at).toLocaleString()}</p>
                    </div>
                    <Badge color={c.state === 'processing' ? 'yellow' : 'green'}>{c.state}</Badge>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
