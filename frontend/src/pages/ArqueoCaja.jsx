import { useState, useEffect } from 'react'
import { reportesApi } from '../services/api'

export default function ArqueoCaja() {
  const [fecha, setFecha] = useState(new Date().toISOString().split('T')[0])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [data, setData] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await reportesApi.arqueoCaja(fecha)
      setData(res.data)
    } catch (err) {
      setError(err.message || 'Error al generar arqueo')
      setData(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    handleSubmit({ preventDefault: () => {} })
  }, [])

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value)
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Arqueo de Caja</h1>
        <p className="text-gray-500">Reporte diario de ingresos por tipo de vehículo</p>
      </div>

      <form onSubmit={handleSubmit} className="card">
        <div className="card-body">
          <div className="flex flex-col sm:flex-row gap-4 items-end">
            <div className="form-group flex-1">
              <label htmlFor="fecha" className="form-label">Fecha</label>
              <input
                type="date"
                id="fecha"
                className="form-input"
                value={fecha}
                onChange={(e) => setFecha(e.target.value)}
                max={new Date().toISOString().split('T')[0]}
                disabled={loading}
              />
            </div>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="loading-spinner" aria-hidden="true"></span>
                  Generando...
                </>
              ) : (
                'Generar Arqueo'
              )}
            </button>
          </div>
        </div>
      </form>

      {error && (
        <div className="alert alert-error" role="alert">
          {error}
        </div>
      )}

      {data && (
        <>
          <div className="card">
            <div className="card-header">
              <h2 className="card-title">Arqueo del {new Date(data.fecha).toLocaleDateString('es-CO', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</h2>
            </div>
            <div className="card-body">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
                <div className="bg-gray-50 rounded-lg p-4 text-center border border-gray-200">
                  <p className="text-xs text-gray-500">Total Vehículos</p>
                  <p className="text-3xl font-bold text-gray-900">{data.totales.total_vehiculos}</p>
                </div>
                <div className="bg-primary-light rounded-lg p-4 text-center border border-primary">
                  <p className="text-xs text-primary">Total Ingresos</p>
                  <p className="text-3xl font-bold text-primary">{formatCurrency(data.totales.total_ingresos)}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4 text-center border border-gray-200">
                  <p className="text-xs text-gray-500">Promedio por Vehículo</p>
                  <p className="text-3xl font-bold text-gray-900">
                    {data.totales.total_vehiculos > 0
                      ? formatCurrency(data.totales.total_ingresos / data.totales.total_vehiculos)
                      : '$0'}
                  </p>
                </div>
              </div>

              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>Tipo de Vehículo</th>
                      <th className="text-right">Cantidad</th>
                      <th className="text-right">Total Ingresos</th>
                      <th className="text-right">Promedio Minutos</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.resumen_por_tipo.map((item, i) => (
                      <tr key={i}>
                        <td>
                          <span className="badge badge-info">{item.tipo_vehiculo}</span>
                        </td>
                        <td className="text-right font-medium">{item.total_vehiculos}</td>
                        <td className="text-right font-semibold text-success">{formatCurrency(item.total_ingresos)}</td>
                        <td className="text-right text-gray-600">{item.promedio_minutos} min</td>
                      </tr>
                    ))}
                    <tr className="bg-gray-50 font-bold">
                      <td>TOTAL</td>
                      <td className="text-right">{data.totales.total_vehiculos}</td>
                      <td className="text-right text-primary">{formatCurrency(data.totales.total_ingresos)}</td>
                      <td className="text-right">—</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <h2 className="card-title">Detalle por Tipo</h2>
            </div>
            <div className="card-body">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                {data.resumen_por_tipo.map((item, i) => (
                  <div key={i} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                    <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                      <span className="badge badge-info">{item.tipo_vehiculo}</span>
                    </h3>
                    <dl className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <dt className="text-gray-500">Vehículos:</dt>
                        <dd className="font-medium">{item.total_vehiculos}</dd>
                      </div>
                      <div className="flex justify-between">
                        <dt className="text-gray-500">Ingresos:</dt>
                        <dd className="font-semibold text-success">{formatCurrency(item.total_ingresos)}</dd>
                      </div>
                      <div className="flex justify-between">
                        <dt className="text-gray-500">Prom. tiempo:</dt>
                        <dd className="text-gray-600">{item.promedio_minutos} min</dd>
                      </div>
                    </dl>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}