import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { vehiculosApi, tarifasApi } from '../services/api'

export default function Dashboard() {
  const [activos, setActivos] = useState([])
  const [tarifas, setTarifas] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const fetchData = async () => {
    try {
      setLoading(true)
      const [activosRes, tarifasRes] = await Promise.all([
        vehiculosApi.getActivos(),
        tarifasApi.listar()
      ])
      setActivos(activosRes.data.vehiculos || [])
      setTarifas(tarifasRes.data.tarifas || [])
      setError('')
    } catch (err) {
      setError(err.message || 'Error al cargar datos')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 30000)
    return () => clearInterval(interval)
  }, [])

  const totalActivos = activos.length
  const motos = activos.filter(v => v.tipo_vehiculo === 'Moto').length
  const carros = activos.filter(v => v.tipo_vehiculo === 'Carro').length
  const camiones = activos.filter(v => v.tipo_vehiculo === 'Camión').length

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="loading-spinner" style={{ width: '2rem', height: '2rem', borderWidth: '3px' }} aria-hidden="true"></div>
        <span className="sr-only">Cargando...</span>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-500">Vista general del parqueadero en tiempo real</p>
        </div>
        <button
          onClick={fetchData}
          disabled={loading}
          className="btn btn-secondary"
        >
          <span className={loading ? 'loading-spinner' : ''} aria-hidden="true"></span>
          Actualizar
        </button>
      </div>

      {error && (
        <div className="alert alert-error" role="alert">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="card">
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Vehículos Activos</p>
                <p className="text-3xl font-bold text-gray-900">{totalActivos}</p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-primary-light flex items-center justify-center">
                <span className="text-2xl">🚗</span>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Motos</p>
                <p className="text-3xl font-bold text-gray-900">{motos}</p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-success-light flex items-center justify-center">
                <span className="text-2xl">🏍️</span>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Carros</p>
                <p className="text-3xl font-bold text-gray-900">{carros}</p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-warning-light flex items-center justify-center">
                <span className="text-2xl">🚗</span>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Camiones</p>
                <p className="text-3xl font-bold text-gray-900">{camiones}</p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-gray-200 flex items-center justify-center">
                <span className="text-2xl">🚚</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Vehículos en el Parqueadero</h2>
          <Link to="/entrada" className="btn btn-primary btn-sm">
            + Nueva Entrada
          </Link>
        </div>
        <div className="card-body p-0">
          {activos.length === 0 ? (
            <div className="text-center py-12">
              <span className="text-4xl mb-4 block">🅿️</span>
              <p className="text-gray-500">No hay vehículos en el parqueadero</p>
              <Link to="/entrada" className="btn btn-primary mt-4 inline-flex">
                Registrar Primera Entrada
              </Link>
            </div>
          ) : (
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Placa</th>
                    <th>Tipo</th>
                    <th>Hora Entrada</th>
                    <th>Tiempo</th>
                    <th>Tarifa/Hora</th>
                    <th>Acumulado</th>
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {activos.map((v) => (
                    <tr key={v.id}>
                      <td className="font-mono font-medium">{v.placa}</td>
                      <td>
                        <span className="badge badge-info">{v.tipo_vehiculo}</span>
                      </td>
                      <td>{new Date(v.hora_entrada).toLocaleString()}</td>
                      <td>{v.minutos_transcurridos} min</td>
                      <td>${Number(v.tarifa_hora).toLocaleString()}</td>
                      <td className="font-semibold text-primary">${Number(v.tarifa_acumulada).toLocaleString()}</td>
                      <td>
                        <Link
                          to={`/salida`}
                          state={{ registro: v }}
                          className="btn btn-sm btn-outline"
                        >
                          Salida
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}