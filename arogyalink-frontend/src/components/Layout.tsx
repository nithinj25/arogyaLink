import { NavLink, Link } from 'react-router-dom'
import { LayoutDashboard, Users, Phone, Heart, ChevronLeft } from 'lucide-react'

const navItems = [
  { to: '/admin',          label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/admin/families', label: 'Families',  icon: Users,           end: false },
  { to: '/admin/cases',    label: 'Cases',     icon: Phone,           end: false },
]

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen overflow-hidden bg-stone-50">
      {/* Sidebar */}
      <aside className="w-56 flex-shrink-0 bg-stone-900 text-white flex flex-col">
        {/* Logo */}
        <div className="px-5 pt-6 pb-5">
          <div className="flex items-center gap-2.5 mb-1">
            <div className="size-7 bg-emergency/20 rounded-lg flex items-center justify-center">
              <Heart className="text-emergency" size={15} />
            </div>
            <p className="font-serif text-[15px] font-semibold tracking-tight">ArogyaLink</p>
          </div>
          <p className="text-stone-500 text-[11px] pl-9">Emergency Dispatch</p>
        </div>

        <span className="block h-[1.5px] bg-white/5 mx-5" />

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-0.5">
          {navItems.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                `flex items-center gap-2.5 px-3 py-2 rounded-xl text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-white/10 text-white'
                    : 'text-stone-500 hover:text-white hover:bg-white/5'
                }`
              }
            >
              <Icon size={15} />
              {label}
            </NavLink>
          ))}
        </nav>

        {/* Back to site + status */}
        <div className="px-5 py-4 space-y-3">
          <Link
            to="/"
            className="flex items-center gap-1.5 text-stone-500 hover:text-white text-xs transition-colors"
          >
            <ChevronLeft size={12} /> Back to site
          </Link>
          <span className="block h-[1.5px] bg-white/5" />
          <div className="flex items-center gap-2">
            <span className="relative flex size-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent-green opacity-75" />
              <span className="relative inline-flex rounded-full size-2 bg-accent-green" />
            </span>
            <span className="text-stone-500 text-[11px]">System operational</span>
          </div>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 overflow-y-auto scrollbar-thin">
        {children}
      </main>
    </div>
  )
}
