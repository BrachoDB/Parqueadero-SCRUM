import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { vehiculosApi, tarifasApi } from '../services/api'

const TIPOS_VEHICULO = [
  { id: 1, nombre: 'Moto', tarifa_hora: 2000 },
  { id: 2, nombre: 'Carro', tarifa_hora: 4000 },
  { id: 3, nombre: 'Camión', tarifa_hora: 7000 }
]

export default function RegistroEntrada() {
  const navigate = useNavigate()
  const [placa, setPlaca] = useState('')
  const [tipoVehiculoId, setTipoVehiculoId] = useState('1')
  const [operadorId, setOperadorId] = useState('')
  const [observaciones, setObservaciones] = useState('')
  const [tarifas, setTarifas] = useState(TIPOS_VEHICULO)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(null)

  useEffect(() => {
    const loadTarifas = async () => {
      try {
        const res = await tarifasApi.listar()
        if (res.data.tarifas?.length) {
          setTarifas(res.data.tarifas)
        }
      } catch (err) {
        console.warn('Usando tarifas por defecto')
      }
    }
    loadTarifas()
  }, [])

  const formatPlaca = (value) => {
    return value.toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 8)
  }

  const handlePlacaChange = (e) => {
    const formatted = formatPlaca(e.target.value)
    setPlaca(formatted)
    setError('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess(null)

    if (!placa || !tipoVehiculoId) {
      setError('Por favor complete todos los campos requeridos')
      return
    }

    if (placa.length < 6) {
      setError('La placa debe tener al menos 6 caracteres')
      return
    }

    setLoading(true)
    try {
      const res = await vehiculosApi.registrarEntrada({
        placa,
        tipo_vehiculo_id: parseInt(tipoVehiculoId),
        operador_id: operadorId ? parseInt(operadorId) : null,
        observaciones: observaciones || null
      })
      setSuccess(res.data)
      setPlaca('')
      setOperadorId('')
      setObservaciones('')
    } catch (err) {
      setError(err.message || 'Error al registrar entrada')
    } finally {
      setLoading(false)
    }
  }

  const selectedTipo = tarifas.find(t => t.id === parseInt(tipoVehiculoId))

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Registrar Entrada</h1>
        <p className="text-gray-500">Ingrese los datos del vehículo que entra al parqueadero</p>
      </div>

      {error && (
        <div className="alert alert-error" role="alert">
          {error}
        </div>
      )}

      {success && (
        <div className="alert alert-success" role="alert">
          <div className="font-medium">✅ Vehículo registrado exitosamente</div>
          <div className="text-sm mt-1">
            ID: {success.id} | Placa: {success.placa} | Tipo: {success.tipo_vehiculo}
          </div>
          <div className="text-sm text-gray-600 mt-1">
            Tarifa: ${Number(success.tarifa_hora).toLocaleString()}/hora | Entrada: {success.hora_entrada}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            Tiempo de respuesta: {success.tiempo_respuesta_ms}ms
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="card">
        <div className="card-body space-y-4">
          <div className="form-group">
            <label htmlFor="placa" className="form-label">Placa *</label>
            <input
              type="text"
              id="placa"
              className="form-input text-uppercase font-mono"
              placeholder="ABC123 o ABC12D"
              value={placa}
              onChange={handlePlacaChange}
              required
              maxLength={8}
              disabled={loading}
              autoFocus
            />
            <p className="text-xs text-gray-500 mt-1">Formato colombiano: AAA000 o AAA00A</p>
          </div>

          <div className="form-group">
            <label htmlFor="tipo_vehiculo" className="form-label">Tipo de Vehículo *</label>
            <select
              id="tipo_vehiculo"
              className="form-select"
              value={tipoVehiculoId}
              onChange={(e) => setTipoVehiculoId(e.target.value)}
              disabled={loading}
              required
            >
              {tarifas.map((tipo) => (
                <option key={tipo.id} value={tipo.id}>
                  {tipo.nombre} - ${Number(tipo.tarifa_hora).toLocaleString()}/hora
                </option>
              ))}
            </select>
          </div>

          {selectedTipo && (
            <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <p className="text-xs text-gray-500">Tarifa por Hora</p>
                  <p className="text-xl font-bold text-gray-900">${Number(selectedTipo.tarifa_hora).toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Tipo</p>
                  <p className="text-lg font-medium text-gray-900">{selectedTipo.nombre}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Descripción</p>
                  <p className="text-sm text-gray-700">{selectedTipo.descripcion || 'N/A'}</p>
                </div>
              </div>
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

          <div className="form-group">
            <label htmlFor="observaciones" className="form-label">Observaciones (opcional)</label>
            <textarea
              id="observaciones"
              className="form-input"
              rows={3}
              placeholder="Observaciones adicionales..."
              value={observaciones}
              onChange={(e) => setObservaciones(e.target.value)}
              disabled={loading}
            />
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="submit"
              className="btn btn-primary flex-1"
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="loading-spinner" aria-hidden="true"></span>
                  Registrando...
                </>
              ) : (
                'Registrar Entrada'
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