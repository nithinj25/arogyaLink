import { Link } from 'react-router-dom'
import { Phone, Brain, MapPin, Activity, Users, Shield, ChevronRight, Heart, Zap, Globe } from 'lucide-react'
import Button from '../components/ui/Button'
import { DividerShort } from '../components/ui/Divider'

const NAV_LINKS = [
  { label: 'How it works', href: '#how-it-works' },
  { label: 'Features', href: '#features' },
  { label: 'Who it serves', href: '#who' },
]

const STEPS = [
  {
    num: '01',
    icon: <Phone size={20} />,
    title: 'Patient calls a single number',
    body: 'Anyone from a rural village dials ArogyaLink. No app, no internet, no literacy required — just a phone call.',
  },
  {
    num: '02',
    icon: <Brain size={20} />,
    title: 'AI triage in the caller\'s language',
    body: 'Our multilingual AI agent speaks Hindi, Kannada, Telugu, and English — asking the right questions to understand the emergency.',
  },
  {
    num: '03',
    icon: <MapPin size={20} />,
    title: 'Location-aware dispatch',
    body: 'The system identifies the nearest PHC, ambulance, and ASHA worker, then simultaneously alerts all relevant parties.',
  },
  {
    num: '04',
    icon: <Activity size={20} />,
    title: 'Real-time monitoring',
    body: 'Coordinators watch every active case live on the dashboard — from first ring to resolution — with full conversation transcript.',
  },
]

const FEATURES = [
  { icon: <Globe size={18} />, title: 'Multilingual IVR', body: 'Hindi, Kannada, Telugu, English. Regional speech recognition with Gemini AI.' },
  { icon: <Brain size={18} />, title: 'Gemini Triage Agent', body: 'Multi-turn conversation that extracts symptom, severity, location, and patient profile automatically.' },
  { icon: <Users size={18} />, title: 'Family Registry', body: 'Pre-register your family. When you call, we already know your address, members, and health history.' },
  { icon: <Zap size={18} />, title: 'Instant Dispatch', body: 'ASHA workers, ambulances, and PHC doctors notified the moment triage completes — no human relay needed.' },
  { icon: <Shield size={18} />, title: 'Offline Resilient', body: 'Works on 2G, works on feature phones, works in zero-connectivity areas via basic call routing.' },
  { icon: <Heart size={18} />, title: 'Human-Centred Design', body: 'Built for panic callers, child callers, and shock victims — the AI handles every edge case gracefully.' },
]

const WHO = [
  { emoji: '👨‍👩‍👧', role: 'Rural Families', desc: 'One number for every health emergency. No forms, no waiting — instant AI-guided help.' },
  { emoji: '🏥', role: 'PHC Doctors', desc: 'Pre-triaged case notes arrive before the patient does. Structured data, not panicked calls.' },
  { emoji: '🤝', role: 'ASHA Workers', desc: 'Automated alerts with location, symptoms, and dispatch instructions on any mobile.' },
  { emoji: '🗂️', role: 'District Coordinators', desc: 'Live dashboard of every active case, historical analytics, and family registry management.' },
]

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-stone-50 text-stone-800 font-sans">
      {/* Nav */}
      <nav className="sticky top-0 z-50 bg-stone-50/90 backdrop-blur border-b border-stone-200">
        <div className="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between">
          <span className="font-serif text-lg font-semibold tracking-tight text-stone-900">ArogyaLink</span>
          <div className="hidden md:flex items-center gap-6">
            {NAV_LINKS.map(l => (
              <a key={l.label} href={l.href} className="text-sm text-stone-600 hover:text-stone-900 transition-colors">{l.label}</a>
            ))}
          </div>
          <Link to="/admin">
            <Button variant="secondary" size="sm">Admin Dashboard <ChevronRight size={14} /></Button>
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="max-w-6xl mx-auto px-6 pt-24 pb-20">
        <div className="max-w-2xl">
          <div className="inline-flex items-center gap-2 text-xs font-medium text-accent-blue bg-blue-50 border border-blue-200 rounded-full px-3 py-1 mb-6">
            <span className="size-1.5 rounded-full bg-accent-blue animate-pulse" />
            Google Solution Challenge 2025
          </div>
          <h1 className="text-5xl md:text-6xl font-serif font-semibold leading-[1.12] tracking-tight text-stone-900 mb-6">
            Emergency healthcare,<br />
            <span className="italic text-stone-500">for every village.</span>
          </h1>
          <DividerShort className="mb-6" />
          <p className="text-lg text-stone-600 leading-relaxed max-w-xl mb-10">
            ArogyaLink connects rural India to emergency healthcare through a single phone call — no internet, no app, no literacy required. Powered by Gemini AI and Google Cloud.
          </p>
          <div className="flex flex-wrap gap-3">
            <a href="tel:+1800000000">
              <Button size="lg" icon={<Phone size={16} />}>
                Call ArogyaLink
              </Button>
            </a>
            <Link to="/admin">
              <Button variant="secondary" size="lg">
                Open Dashboard
              </Button>
            </Link>
          </div>
        </div>

        {/* Stats strip */}
        <div className="mt-20 grid grid-cols-2 md:grid-cols-4 gap-px bg-stone-200 rounded-2xl overflow-hidden border border-stone-200">
          {[
            { value: '4', label: 'Languages supported' },
            { value: '<3s', label: 'AI triage response' },
            { value: '24/7', label: 'Always available' },
            { value: '2G', label: 'Works on basic networks' },
          ].map(s => (
            <div key={s.label} className="bg-white px-6 py-5">
              <p className="font-serif text-3xl font-semibold text-stone-900">{s.value}</p>
              <p className="text-xs text-stone-500 mt-1">{s.label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section id="how-it-works" className="bg-white border-y border-stone-200 py-20">
        <div className="max-w-6xl mx-auto px-6">
          <p className="text-xs font-semibold text-stone-400 uppercase tracking-widest mb-3">How it works</p>
          <h2 className="font-serif text-4xl font-semibold text-stone-900 mb-2">From panic call to dispatch<br /><span className="italic font-normal text-stone-500">in under 90 seconds.</span></h2>
          <DividerShort className="mt-6 mb-14" />

          <div className="grid md:grid-cols-4 gap-8">
            {STEPS.map((step, i) => (
              <div key={step.num} className="relative">
                {i < STEPS.length - 1 && (
                  <span className="hidden md:block absolute top-5 left-[calc(100%+8px)] w-[calc(100%-16px)] h-[1.5px] bg-stone-200" />
                )}
                <div className="flex items-center gap-3 mb-4">
                  <div className="size-10 rounded-full bg-stone-900 text-white flex items-center justify-center shrink-0">
                    {step.icon}
                  </div>
                  <span className="text-xs font-semibold text-stone-400 tabular-nums">{step.num}</span>
                </div>
                <h3 className="font-semibold text-stone-900 text-sm mb-2">{step.title}</h3>
                <p className="text-sm text-stone-500 leading-relaxed">{step.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-20">
        <div className="max-w-6xl mx-auto px-6">
          <p className="text-xs font-semibold text-stone-400 uppercase tracking-widest mb-3">Features</p>
          <h2 className="font-serif text-4xl font-semibold text-stone-900 mb-2">Built for the last mile,<br /><span className="italic font-normal text-stone-500">without compromise.</span></h2>
          <DividerShort className="mt-6 mb-14" />

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-px bg-stone-200 rounded-2xl overflow-hidden border border-stone-200">
            {FEATURES.map(f => (
              <div key={f.title} className="bg-white p-6 hover:bg-stone-50 transition-colors">
                <div className="size-9 rounded-xl bg-stone-100 flex items-center justify-center text-stone-700 mb-4">
                  {f.icon}
                </div>
                <h3 className="font-semibold text-stone-900 text-sm mb-1.5">{f.title}</h3>
                <p className="text-sm text-stone-500 leading-relaxed">{f.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Who it serves */}
      <section id="who" className="bg-stone-900 text-white py-20">
        <div className="max-w-6xl mx-auto px-6">
          <p className="text-xs font-semibold text-stone-400 uppercase tracking-widest mb-3">Who it serves</p>
          <h2 className="font-serif text-4xl font-semibold mb-2">One system,<br /><span className="italic font-normal text-stone-400">four stakeholders.</span></h2>
          <DividerShort className="mt-6 mb-14" />

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {WHO.map(w => (
              <div key={w.role} className="bg-stone-800 rounded-2xl p-5 border border-stone-700">
                <div className="text-3xl mb-4">{w.emoji}</div>
                <h3 className="font-semibold text-white text-sm mb-2">{w.role}</h3>
                <p className="text-sm text-stone-400 leading-relaxed">{w.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 bg-white border-t border-stone-200">
        <div className="max-w-xl mx-auto px-6 text-center">
          <h2 className="font-serif text-4xl font-semibold text-stone-900 mb-4">Ready to deploy?</h2>
          <p className="text-stone-500 mb-8 leading-relaxed">
            ArogyaLink is open-source and built for district health administrators. Register your first PHC and go live in minutes.
          </p>
          <div className="flex flex-wrap gap-3 justify-center">
            <Link to="/admin">
              <Button size="lg">Open Admin Dashboard <ChevronRight size={15} /></Button>
            </Link>
            <a href="https://github.com" target="_blank" rel="noopener noreferrer">
              <Button variant="secondary" size="lg">View on GitHub</Button>
            </a>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-stone-200 py-8">
        <div className="max-w-6xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-3">
          <span className="font-serif text-sm text-stone-600">ArogyaLink — Emergency Healthcare for Rural India</span>
          <p className="text-xs text-stone-400">Built for Google Solution Challenge 2025 · Powered by Gemini & Google Cloud</p>
        </div>
      </footer>
    </div>
  )
}
