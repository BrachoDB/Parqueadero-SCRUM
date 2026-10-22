import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useState } from 'react'

const navItems = [
  { path: '/dashboard', label: 'Dashboard', icon: '📊' },
  { path: '/entrada', label: 'Registrar Entrada', icon: '🚗' },
  { path: '/salida', label: 'Registrar Salida', icon: '🚙' },
  { path: '/tarifa', label: 'Consultar Tarifa', icon: '💰' },
  { path: '/tarifas', label: 'Tarifas', icon: '🏷️' },
  { path: '/arqueo', label: 'Arqueo de Caja', icon: '📋' }
]

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const navigate = useNavigate()

  const handleLogout = () => {
    localStorage.removeItem('auth_token')
    navigate('/login')
  }

  return (
    <div className="flex min-h-screen bg-gray-50">
      <aside className={`fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-gray-200 transform transition-transform duration-300 lg:translate-x-0 ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      }`}>
        <div className="flex h-16 items-center justify-between px-4 border-b border-gray-200">
          <h1 className="text-xl font-bold text-gray-900">Parqueadero</h1>
          <button
            className="lg:hidden p-2 text-gray-500 hover:text-gray-700"
            onClick={() => setSidebarOpen(false)}
            aria-label="Cerrar menú"
          >
            ✕
          </button>
        </div>
        <nav className="p-4 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-primary-light text-primary'
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                }`
              }
              onClick={() => setSidebarOpen(false)}
            >
              <span>{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200">
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-100 hover:text-gray-900 transition-colors"
          >
            <span>🚪</span>
            Cerrar Sesión
          </button>
        </div>
      </aside>

      <div className="flex-1 lg:ml-64">
        <header className="sticky top-0 z-40 h-16 bg-white border-b border-gray-200">
          <div className="flex h-full items-center justify-between px-4">
            <button
              className="lg:hidden p-2 text-gray-500 hover:text-gray-700"
              onClick={() => setSidebarOpen(true)}
              aria-label="Abrir menú"
            >
              ☰
            </button>
            <div className="flex-1 lg:flex-none">
              <h2 className="text-lg font-semibold text-gray-900">Sistema de Gestión de Parqueaderos</h2>
            </div>
            <div className="flex items-center gap-4">
              <span className="hidden sm:block text-sm text-gray-500">Operador: Admin</span>
            </div>
          </div>
        </header>
        <main className="p-4 lg:p-6">
          <Outlet />
        </main>
      </div>

      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
          aria-hidden="true"
        />
      )}
    </div>
  )
}