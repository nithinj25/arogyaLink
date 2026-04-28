import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Trash2, ChevronLeft, User } from 'lucide-react'
import { createFamily } from '../lib/api'
import type { FamilyMember, Language } from '../lib/types'
import Button from '../components/ui/Button'
import Input from '../components/ui/Input'

const RELATIONSHIPS = ['self', 'spouse', 'father', 'mother', 'son', 'daughter', 'sibling', 'grandparent', 'other']
const COMMON_CONDITIONS = ['Diabetes', 'Hypertension', 'Heart Disease', 'Asthma', 'Epilepsy', 'Kidney Disease', 'Cancer', 'TB', 'Arthritis']
const BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

const emptyMember = (): Omit<FamilyMember, 'id'> => ({
  name: '', age: 0, gender: 'M', relationship: 'self',
  conditions: [], allergies: [], blood_group: null, medications: [],
})

const fieldClass = 'w-full border border-stone-200 rounded-xl px-3 py-2 text-sm bg-white text-stone-900 placeholder-stone-400 focus:outline-none focus:border-stone-400 transition-colors'

export default function RegisterFamilyPage() {
  const nav = useNavigate()
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const [form, setForm] = useState({
    primary_name: '', phone: '', address: '', village: '',
    district: '', state: '', pin: '', language: 'en-IN' as Language,
    members: [{ ...emptyMember() }],
  })

  const setField = (k: string, v: unknown) => setForm(f => ({ ...f, [k]: v }))
  const setMember = (i: number, k: string, v: unknown) =>
    setForm(f => { const members = [...f.members]; members[i] = { ...members[i], [k]: v }; return { ...f, members } })
  const toggleCondition = (i: number, cond: string) => {
    const cur = form.members[i].conditions
    setMember(i, 'conditions', cur.includes(cond) ? cur.filter(c => c !== cond) : [...cur, cond])
  }
  const addMember = () => setForm(f => ({ ...f, members: [...f.members, { ...emptyMember() }] }))
  const removeMember = (i: number) => setForm(f => ({ ...f, members: f.members.filter((_, idx) => idx !== i) }))

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.primary_name || !form.phone) { setError('Name and phone are required.'); return }
    setSaving(true); setError('')
    try {
      const payload = { ...form, pin: form.pin || null, members: form.members.map((m, i) => ({ ...m, id: `m${i}` })) }
      const saved = await createFamily(payload)
      nav(`/admin/families/${encodeURIComponent(saved.phone)}`)
    } catch (err: unknown) {
      setError((err as Error).message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="p-7 max-w-3xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-3 mb-7">
        <button onClick={() => nav(-1)} className="size-8 rounded-xl text-stone-500 hover:bg-stone-100 flex items-center justify-center transition-colors">
          <ChevronLeft size={18} />
        </button>
        <div>
          <p className="text-xs font-semibold text-stone-400 uppercase tracking-widest mb-0.5">Registry</p>
          <h1 className="font-serif text-2xl font-semibold text-stone-900">Register Family</h1>
        </div>
      </div>

      <span className="divider-full block mb-7" />

      <form onSubmit={handleSubmit} className="space-y-5">
        {/* Primary contact */}
        <section className="bg-white border border-stone-200 rounded-2xl p-5">
          <h2 className="text-xs font-semibold text-stone-400 uppercase tracking-widest mb-4">Primary Contact</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input label="Full Name *" required value={form.primary_name} onChange={e => setField('primary_name', e.target.value)} />
            <Input label="Phone Number *" required value={form.phone} onChange={e => setField('phone', e.target.value)} placeholder="+91 98765 43210" />
            <div>
              <label className="block text-xs font-medium text-stone-600 mb-1.5">Preferred Language</label>
              <select value={form.language} onChange={e => setField('language', e.target.value)} className={fieldClass}>
                <option value="en-IN">English</option>
                <option value="hi-IN">Hindi</option>
                <option value="kn-IN">Kannada</option>
                <option value="te-IN">Telugu</option>
              </select>
            </div>
          </div>
        </section>

        {/* Address */}
        <section className="bg-white border border-stone-200 rounded-2xl p-5">
          <h2 className="text-xs font-semibold text-stone-400 uppercase tracking-widest mb-4">Home Address</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="sm:col-span-2">
              <Input label="Street / Landmark" value={form.address} onChange={e => setField('address', e.target.value)} />
            </div>
            <Input label="Village / Town *" required value={form.village} onChange={e => setField('village', e.target.value)} />
            <Input label="District *"       required value={form.district} onChange={e => setField('district', e.target.value)} />
            <Input label="State *"          required value={form.state} onChange={e => setField('state', e.target.value)} />
            <Input label="PIN Code"                  value={form.pin} onChange={e => setField('pin', e.target.value)} />
          </div>
        </section>

        {/* Family members */}
        <section className="bg-white border border-stone-200 rounded-2xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xs font-semibold text-stone-400 uppercase tracking-widest">Family Members</h2>
            <button type="button" onClick={addMember}
              className="flex items-center gap-1.5 text-xs font-medium text-stone-600 hover:text-stone-900 transition-colors">
              <Plus size={13} /> Add Member
            </button>
          </div>

          <div className="space-y-4">
            {form.members.map((m, i) => (
              <div key={i} className="border border-stone-100 rounded-xl p-4 bg-stone-50/50 relative">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <div className="size-7 rounded-full bg-stone-200 flex items-center justify-center">
                      <User size={13} className="text-stone-600" />
                    </div>
                    <span className="text-sm font-medium text-stone-700">Member {i + 1}</span>
                  </div>
                  {form.members.length > 1 && (
                    <button type="button" onClick={() => removeMember(i)} className="text-stone-400 hover:text-emergency transition-colors">
                      <Trash2 size={14} />
                    </button>
                  )}
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <div className="col-span-2">
                    <Input label="Name *" required value={m.name} onChange={e => setMember(i, 'name', e.target.value)} />
                  </div>
                  <div>
                    <Input label="Age" type="number" min={0} max={120} value={m.age || ''} onChange={e => setMember(i, 'age', Number(e.target.value))} />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-stone-600 mb-1.5">Gender</label>
                    <select value={m.gender} onChange={e => setMember(i, 'gender', e.target.value)} className={fieldClass}>
                      <option value="M">Male</option>
                      <option value="F">Female</option>
                      <option value="other">Other</option>
                    </select>
                  </div>
                  <div className="col-span-2">
                    <label className="block text-xs font-medium text-stone-600 mb-1.5">Relationship</label>
                    <select value={m.relationship} onChange={e => setMember(i, 'relationship', e.target.value)} className={fieldClass}>
                      {RELATIONSHIPS.map(r => <option key={r} value={r}>{r.charAt(0).toUpperCase() + r.slice(1)}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-stone-600 mb-1.5">Blood Group</label>
                    <select value={m.blood_group ?? ''} onChange={e => setMember(i, 'blood_group', e.target.value || null)} className={fieldClass}>
                      <option value="">Unknown</option>
                      {BLOOD_GROUPS.map(g => <option key={g} value={g}>{g}</option>)}
                    </select>
                  </div>

                  <div className="col-span-2 sm:col-span-4">
                    <label className="block text-xs font-medium text-stone-600 mb-2">Medical Conditions</label>
                    <div className="flex flex-wrap gap-1.5">
                      {COMMON_CONDITIONS.map(cond => (
                        <button key={cond} type="button" onClick={() => toggleCondition(i, cond)}
                          className={`text-xs px-2.5 py-1 rounded-full border transition-colors ${
                            m.conditions.includes(cond)
                              ? 'bg-emergency/10 text-red-700 border-red-200'
                              : 'bg-white text-stone-600 border-stone-200 hover:border-stone-300'
                          }`}>
                          {cond}
                        </button>
                      ))}
                    </div>
                    <input value={m.conditions.filter(c => !COMMON_CONDITIONS.includes(c)).join(', ')}
                      onChange={e => {
                        const custom = e.target.value.split(',').map(s => s.trim()).filter(Boolean)
                        const known = m.conditions.filter(c => COMMON_CONDITIONS.includes(c))
                        setMember(i, 'conditions', [...known, ...custom])
                      }}
                      placeholder="Other conditions (comma-separated)"
                      className="mt-2 w-full border border-stone-200 rounded-xl px-3 py-1.5 text-xs bg-white focus:outline-none focus:border-stone-400 transition-colors" />
                  </div>

                  <div className="col-span-2 sm:col-span-4">
                    <Input label="Allergies" value={m.allergies.join(', ')}
                      onChange={e => setMember(i, 'allergies', e.target.value.split(',').map(s => s.trim()).filter(Boolean))}
                      placeholder="e.g. Penicillin, Peanuts" />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {error && (
          <div className="bg-red-50 border border-red-200 text-emergency text-sm rounded-xl px-4 py-3">{error}</div>
        )}

        <div className="flex gap-3">
          <Button type="button" variant="secondary" fullWidth onClick={() => nav(-1)}>Cancel</Button>
          <Button type="submit" fullWidth loading={saving}>{saving ? 'Registering…' : 'Register Family'}</Button>
        </div>
      </form>
    </div>
  )
}
