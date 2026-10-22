import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { vehiculosApi } from '../services/api'

export default function ConsultaTarifa() {
  const { placa } = useParams()
  const navigate = useNavigate()
  const [placaInput, setPlacaInput] = useState(placa || '')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [data, setData] = useState(null)
  const [slaHistory, setSlaHistory] = useState([])

  const formatPlaca = (value) => {
    return value.toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 8)
  }

  const handlePlacaChange = (e) => {
    const formatted = formatPlaca(e.target.value)
    setPlacaInput(formatted)
    setError('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (!placaInput || placaInput.length < 6) {
      setError('Ingrese una placa válida (mínimo 6 caracteres)')
      return
    }

    setLoading(true)
    try {
      const res = await vehiculosApi.consultarTarifa(placaInput)
      setData(res.data)
      setSlaHistory(prev => [
        { placa: res.data.placa, tiempo: res.data.tiempo_respuesta_ms, cumple: res.data.cumple_sla, timestamp: new Date() },
        ...prev.slice(0, 9)
      ])
    } catch (err) {
      setError(err.message || 'Error al consultar tarifa')
      setData(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (placa) {
      handleSubmit({ preventDefault: () => {} })
    }
  }, [placa])

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Consultar Tarifa Acumulada</h1>
        <p className="text-gray-500">Verifique el tiempo y costo actual de un vehículo en el parqueadero</p>
      </div>

      <form onSubmit={handleSubmit} className="card">
        <div className="card-body space-y-4">
          <div className="form-group">
            <label htmlFor="placa" className="form-label">Placa *</label>
            <div className="flex gap-2">
              <input
                type="text"
                id="placa"
                className="form-input text-uppercase font-mono flex-1"
                placeholder="ABC123"
                value={placaInput}
                onChange={handlePlacaChange}
                required
                maxLength={8}
                disabled={loading}
                autoFocus
              />
              <button
                type="submit"
                className="btn btn-primary"
                disabled={loading || !placaInput || placaInput.length < 6}
              >
                {loading ? (
                  <span className="loading-spinner" aria-hidden="true"></span>
                ) : (
                  'Consultar'
                )}
              </button>
            </div>
            <p className="text-xs text-gray-500 mt-1">Formato colombiano: AAA000 o AAA00A</p>
          </div>
        </div>
      </form>

      {error && (
        <div className="alert alert-error" role="alert">
          {error}
        </div>
      )}

      {data && (
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">
              {data.placa} - {data.tipo_vehiculo}
              <span className={`badge ${data.cumple_sla ? 'badge-success' : 'badge-danger'} ml-2`}>
                {data.cumple_sla ? '✓ SLA OK' : '✗ SLA Violado'}
              </span>
            </h2>
          </div>
          <div className="card-body">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              <div className="bg-gray-50 rounded-lg p-4 text-center">
                <p className="text-xs text-gray-500">Hora Entrada</p>
                <p className="text-lg font-semibold text-gray-900">{new Date(data.hora_entrada).toLocaleString()}</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-4 text-center">
                <p className="text-xs text-gray-500">Minutos Transcurridos</p>
                <p className="text-lg font-semibold text-gray-900">{data.minutos_transcurridos}</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-4 text-center">
                <p className="text-xs text-gray-500">Tarifa/Hora</p>
                <p className="text-lg font-semibold text-gray-900">${Number(data.tarifa_hora).toLocaleString()}</p>
              </div>
              <div className="bg-primary-light rounded-lg p-4 text-center">
                <p className="text-xs text-primary">Tarifa Acumulada</p>
                <p className="text-2xl font-bold text-primary">${Number(data.tarifa_acumulada).toLocaleString()}</p>
              </div>
            </div>

            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Tiempo de respuesta API</span>
                <span className={`font-mono font-semibold ${data.cumple_sla ? 'text-success' : 'text-danger'}`}>
                  {data.tiempo_respuesta_ms} ms
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                <div
                  className={`h-2 rounded-full transition-all ${data.cumple_sla ? 'bg-success' : 'bg-danger'}`}
                  style={{ width: `${Math.min(100, (data.tiempo_respuesta_ms / 2000) * 100)}%` }}
                ></div>
              </div>
              <p className="text-xs text-gray-500 mt-1 text-right">
                Límite SLA: 2000 ms
              </p>
            </div>

            <div className="mt-4 flex gap-2">
              <Link to={`/salida`} state={{ registro: { id: data.id, placa: data.placa, tipo_vehiculo: data.tipo_vehiculo } }} className="btn btn-success">
                Registrar Salida
              </Link>
              <button
                onClick={handleSubmit}
                disabled={loading}
                className="btn btn-secondary"
              >
                Actualizar
              </button>
            </div>
          </div>
        </div>
      )}

      {slaHistory.length > 0 && (
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Historial de Consultas (Últimas 10)</h2>
          </div>
          <div className="card-body p-0">
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Placa</th>
                    <th>Tiempo (ms)</th>
                    <th>SLA</th>
                    <th>Hora</th>
                  </tr>
                </thead>
                <tbody>
                  {slaHistory.map((item, i) => (
                    <tr key={i}>
                      <td className="font-mono">{item.placa}</td>
                      <td>{item.tiempo.toFixed(2)}</td>
                      <td>
                        <span className={`badge ${item.cumple ? 'badge-success' : 'badge-danger'}`}>
                          {item.cumple ? 'OK' : 'Violado'}
                        </span>
                      </td>
                      <td>{item.timestamp.toLocaleTimeString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}