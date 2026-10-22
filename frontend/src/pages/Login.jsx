import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function Login() {
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    await new Promise(resolve => setTimeout(resolve, 500))

    if (username && password) {
      localStorage.setItem('auth_token', 'demo-token')
      navigate('/dashboard')
    } else {
      setError('Por favor ingrese usuario y contraseña')
    }
    setLoading(false)
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md">
        <div className="card">
          <div className="card-body">
            <div className="text-center mb-8">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-primary-light text-primary mb-4">
                <span className="text-3xl">🅿️</span>
              </div>
              <h1 className="text-2xl font-bold text-gray-900">Sistema de Parqueadero</h1>
              <p className="text-gray-500 mt-1">Inicie sesión para continuar</p>
            </div>

            {error && (
              <div className="alert alert-error" role="alert">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="form-group">
                <label htmlFor="username" className="form-label">Usuario</label>
                <input
                  type="text"
                  id="username"
                  className="form-input"
                  placeholder="Ingrese su usuario"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  autoComplete="username"
                  disabled={loading}
                />
              </div>

              <div className="form-group">
                <label htmlFor="password" className="form-label">Contraseña</label>
                <input
                  type="password"
                  id="password"
                  className="form-input"
                  placeholder="Ingrese su contraseña"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  autoComplete="current-password"
                  disabled={loading}
                />
              </div>

              <button
                type="submit"
                className="btn btn-primary w-full"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <span className="loading-spinner" aria-hidden="true"></span>
                    Iniciando sesión...
                  </>
                ) : (
                  'Iniciar Sesión'
                )}
              </button>
            </form>

            <div className="mt-6 text-center text-sm text-gray-500">
              <p>Demo: cualquier usuario/contraseña</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}