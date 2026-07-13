import { Outlet, NavLink } from 'react-router-dom'
import { BookOpen, Search, Layers, Plus, Home } from 'lucide-react'

const navItems = [
  { to: '/', label: 'Dashboard', icon: Home },
  { to: '/records', label: 'Records', icon: Layers },
  { to: '/search', label: 'Search', icon: Search },
]

const RootLayout = () => {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="border-b border-slate-800 bg-slate-900/90 backdrop-blur-md">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <BookOpen className="h-8 w-8 text-cyan-400" />
            <div>
              <p className="text-lg font-semibold">Open Research Repository</p>
              <p className="text-sm text-slate-400">Search and manage research records</p>
            </div>
          </div>
          <nav className="hidden items-center gap-4 md:flex">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center gap-2 rounded-full px-4 py-2 text-sm transition ${
                    isActive ? 'bg-cyan-500/20 text-cyan-200' : 'text-slate-300 hover:bg-slate-800/80'
                  }`
                }
              >
                <item.icon className="h-4 w-4" />
                {item.label}
              </NavLink>
            ))}
            <NavLink
              to="/records/new"
              className="hidden items-center gap-2 rounded-full bg-cyan-500 px-4 py-2 text-sm text-slate-950 transition hover:bg-cyan-400 md:flex"
            >
              <Plus className="h-4 w-4" />
              New Record
            </NavLink>
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <Outlet />
      </main>

      <footer className="border-t border-slate-800 bg-slate-900/80 px-4 py-6 text-sm text-slate-500 sm:px-6 lg:px-8">
        <div className="mx-auto flex max-w-7xl flex-col gap-2 md:flex-row md:items-center md:justify-between">
          <p>Open Research Repository UI</p>
          <p>Built with React, Vite, Tailwind, TanStack Query, and Axios.</p>
        </div>
      </footer>
    </div>
  )
}

export default RootLayout
