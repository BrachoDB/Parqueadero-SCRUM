import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { vehiculosApi } from '../services/api'

export default function RegistroSalida() {
  const navigate = useNavigate()
  const location = useLocation()
  const [registroId, setRegistroId] = useState('')
  const [operadorId, setOperadorId] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(null)
  const [activos, setActivos] = useState([])
  const [showDropdown, setShowDropdown] = useState(false)

  const prefilledRegistro = location.state?.registro

  useEffect(() => {
    if (prefilledRegistro) {
      setRegistroId(prefilledRegistro.id.toString())
      setShowDropdown(false)
    }
    loadActivos()
  }, [prefilledRegistro])

  const loadActivos = async () => {
    try {
      const res = await vehiculosApi.getActivos()
      setActivos(res.data.vehiculos || [])
    } catch (err) {
      console.warn('No se pudieron cargar vehículos activos')
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess(null)

    if (!registroId) {
      setError('Seleccione un vehículo')
      return
    }

    setLoading(true)
    try {
      const res = await vehiculosApi.registrarSalida({
        registro_id: parseInt(registroId),
        operador_id: operadorId ? parseInt(operadorId) : null
      })
      setSuccess(res.data)
      setRegistroId('')
      setOperadorId('')
      setShowDropdown(false)
      loadActivos()
    } catch (err) {
      setError(err.message || 'Error al registrar salida')
    } finally {
      setLoading(false)
    }
  }

  const getPlacaDisplay = (id) => {
    const v = activos.find(v => v.id === parseInt(id))
    return v ? `${v.placa} (${v.tipo_vehiculo})` : ''
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Registrar Salida</h1>
        <p className="text-gray-500">Liquide el cobro del vehículo que sale del parqueadero</p>
      </div>

      {error && (
        <div className="alert alert-error" role="alert">
          {error}
        </div>
      )}

      {success && (
        <div className="alert alert-success" role="alert">
          <div className="font-medium">✅ Vehículo liquidado exitosamente</div>
          <div className="grid grid-cols-2 gap-2 text-sm mt-2">
            <div><span className="text-gray-500">Placa:</span> <span className="font-medium">{success.placa}</span></div>
            <div><span className="text-gray-500">Tipo:</span> <span className="font-medium">{success.tipo_vehiculo}</span></div>
            <div><span className="text-gray-500">Entrada:</span> <span className="font-medium">{success.hora_entrada}</span></div>
            <div><span className="text-gray-500">Salida:</span> <span className="font-medium">{success.hora_salida}</span></div>
            <div><span className="text-gray-500">Minutos:</span> <span className="font-medium">{success.minutos_parqueado}</span></div>
            <div><span className="text-gray-500">Horas cobradas:</span> <span className="font-medium">{success.horas_cobradas}</span></div>
            <div className="col-span-2"><span className="text-gray-500">Tarifa/hora:</span> <span className="font-medium">${Number(success.tarifa_hora).toLocaleString()}</span></div>
            <div className="col-span-2"><span className="text-gray-500">Total cobrado:</span> <span className="text-xl font-bold text-success">${Number(success.total_cobrado).toLocaleString()}</span></div>
          </div>
          <div className="text-xs text-gray-500 mt-2">
            Tiempo de respuesta: {success.tiempo_respuesta_ms}ms
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="card">
        <div className="card-body space-y-4">
          <div className="form-group relative">
            <label htmlFor="registro_id" className="form-label">Vehículo *</label>
            <div className="relative">
              <select
                id="registro_id"
                className="form-select pr-10 appearance-none"
                value={registroId}
                onChange={(e) => {
                  setRegistroId(e.target.value)
                  setShowDropdown(false)
                }}
                onFocus={() => setShowDropdown(true)}
                onBlur={() => setTimeout(() => setShowDropdown(false), 200)}
                disabled={loading}
                required
              >
                <option value="">Seleccione un vehículo activo</option>
                {activos.map((v) => (
                  <option key={v.id} value={v.id}>
                    {v.placa} - {v.tipo_vehiculo} - Entrada: {new Date(v.hora_entrada).toLocaleTimeString()} - ${Number(v.tarifa_acumulada).toLocaleString()}
                  </option>
                ))}
              </select>
              <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </div>
            {activos.length === 0 && (
              <p className="text-xs text-gray-500 mt-1">No hay vehículos activos. Registre una entrada primero.</p>
            )}
          </div>

          {registroId && (
            <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <p className="text-sm font-medium text-gray-900">
                Vehículo: <span className="font-mono">{getPlacaDisplay(registroId)}</span>
              </p>
              <p className="text-sm text-gray-600 mt-1">
                El cobro se calculará automáticamente al registrar la salida (hora iniciada = hora cobrada)
              </p>
            </div>
          )}

          <div className="form-group">
            <label htmlFor="operador_id" className="form-label">ID Operador (opcional)</label>
            <input
              type="number"
              id="operador_id"
              className="form-input"
              placeholder="Ej: 1"
              value={operadorId}
              onChange={(e) => setOperadorId(e.target.value)}
              min="1"
              disabled={loading}
            />
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="submit"
              className="btn btn-success flex-1"
              disabled={loading || !registroId}
            >
              {loading ? (
                <>
                  <span className="loading-spinner" aria-hidden="true"></span>
                  Procesando...
                </>
              ) : (
                'Registrar Salida y Cobrar'
              )}
            </button>
            <button
              type="button"
              onClick={() => navigate('/dashboard')}
              className="btn btn-secondary"
              disabled={loading}
            >
              Volver
            </button>
          </div>
        </div>
      </form>
    </div>
  )
}