import { useState, useEffect } from 'react'
import { tarifasApi } from '../services/api'

const TIPOS_DEFAULT = [
  { id: 1, nombre: 'Moto', tarifa_hora: 2000, descripcion: 'Motocicletas y bicimotos' },
  { id: 2, nombre: 'Carro', tarifa_hora: 4000, descripcion: 'Automóviles particulares y taxis' },
  { id: 3, nombre: 'Camión', tarifa_hora: 7000, descripcion: 'Vehículos de carga y buses' }
]

export default function Tarifas() {
  const [tarifas, setTarifas] = useState(TIPOS_DEFAULT)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [editingId, setEditingId] = useState(null)
  const [editForm, setEditForm] = useState({ nombre: '', tarifa_hora: '', descripcion: '' })

  useEffect(() => {
    const loadTarifas = async () => {
      try {
        const res = await tarifasApi.listar()
        if (res.data.tarifas?.length) {
          setTarifas(res.data.tarifas)
        }
        setError('')
      } catch (err) {
        setError('No se pudieron cargar las tarifas del servidor. Mostrando valores por defecto.')
      } finally {
        setLoading(false)
      }
    }
    loadTarifas()
  }, [])

  const startEdit = (tarifa) => {
    setEditingId(tarifa.id)
    setEditForm({
      nombre: tarifa.nombre,
      tarifa_hora: tarifa.tarifa_hora.toString(),
      descripcion: tarifa.descripcion || ''
    })
  }

  const cancelEdit = () => {
    setEditingId(null)
    setEditForm({ nombre: '', tarifa_hora: '', descripcion: '' })
  }

  const saveEdit = async (id) => {
    setError('Función de edición requiere endpoint PUT en el backend (no implementado en esta demo)')
    cancelEdit()
  }

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value)
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Tarifas Diferenciales</h1>
          <p className="text-gray-500">Configuración de tarifas por tipo de vehículo (RF-02)</p>
        </div>
        {loading && (
          <div className="loading-spinner" style={{ width: '1.5rem', height: '1.5rem', borderWidth: '2px' }} aria-hidden="true"></div>
        )}
      </div>

      {error && (
        <div className="alert alert-warning" role="alert">
          ⚠️ {error}
        </div>
      )}

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Tipos de Vehículo Configurados</h2>
        </div>
        <div className="card-body p-0">
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Tipo</th>
                  <th>Descripción</th>
                  <th className="text-right">Tarifa/Hora</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {tarifas.map((tarifa) => (
                  <tr key={tarifa.id}>
                    {editingId === tarifa.id ? (
                      <td colSpan={4} className="p-4">
                        <div className="flex flex-col sm:flex-row gap-3">
                          <input
                            type="text"
                            className="form-input"
                            value={editForm.nombre}
                            onChange={(e) => setEditForm({ ...editForm, nombre: e.target.value })}
                            placeholder="Nombre"
                          />
                          <input
                            type="number"
                            className="form-input"
                            value={editForm.tarifa_hora}
                            onChange={(e) => setEditForm({ ...editForm, tarifa_hora: e.target.value })}
                            placeholder="Tarifa/hora"
                            min="0"
                            step="100"
                          />
                          <input
                            type="text"
                            className="form-input"
                            value={editForm.descripcion}
                            onChange={(e) => setEditForm({ ...editForm, descripcion: e.target.value })}
                            placeholder="Descripción"
                          />
                          <div className="flex gap-2">
                            <button
                              onClick={() => saveEdit(tarifa.id)}
                              className="btn btn-success btn-sm"
                            >
                              Guardar
                            </button>
                            <button
                              onClick={cancelEdit}
                              className="btn btn-secondary btn-sm"
                            >
                              Cancelar
                            </button>
                          </div>
                        </div>
                      </td>
                    ) : (
                      <>
                        <td className="font-medium">{tarifa.nombre}</td>
                        <td className="text-gray-600">{tarifa.descripcion || '—'}</td>
                        <td className="text-right font-semibold text-primary">{formatCurrency(tarifa.tarifa_hora)}</td>
                        <td>
                          <button
                            onClick={() => startEdit(tarifa)}
                            className="btn btn-outline btn-sm"
                            title="Editar (requiere backend)"
                          >
                            Editar
                          </button>
                        </td>
                      </>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Reglas de Cobro (RF-03)</h2>
        </div>
        <div className="card-body">
          <ul className="space-y-3 text-gray-700">
            <li className="flex items-start gap-3">
              <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary-light text-primary text-xs flex items-center justify-center font-bold">1</span>
              <span>El cobro se calcula por <strong>hora iniciada</strong> (techo matemático): <code className="bg-gray-100 px-1.5 py-0.5 rounded text-sm">ceil(minutos / 60) × tarifa_hora</code></span>
            </li>
            <li className="flex items-start gap-3">
              <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary-light text-primary text-xs flex items-center justify-center font-bold">2</span>
              <span>Si un vehículo está <strong>menos de 1 hora</strong>, se cobra 1 hora completa</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary-light text-primary text-xs flex items-center justify-center font-bold">3</span>
              <span>Ejemplo: 61 minutos = 2 horas cobradas | 120 minutos = 2 horas cobradas | 121 minutos = 3 horas cobradas</span>
            </li>
          </ul>

          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <h3 className="font-semibold text-gray-900 mb-3">Ejemplos de cálculo</h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
              {[
                { tipo: 'Moto', tarifa: 2000, minutos: 45, horas: 1, total: 2000 },
                { tipo: 'Carro', tarifa: 4000, minutos: 90, horas: 2, total: 8000 },
                { tipo: 'Camión', tarifa: 7000, minutos: 180, horas: 3, total: 21000 }
              ].map((ej, i) => (
                <div key={i} className="bg-white p-3 rounded border border-gray-200">
                  <p className="font-medium text-gray-900">{ej.tipo}</p>
                  <p className="text-gray-600">{ej.minutos} min → {ej.horas} hora(s) cobrada(s)</p>
                  <p className="font-semibold text-primary mt-1">{formatCurrency(ej.total)}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Rendimiento SLA (RF-01 Rendimiento)</h2>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="bg-success-light border border-success p-4 rounded-lg">
              <h3 className="font-semibold text-success mb-2">✓ Consulta Tarifa ≤ 2s</h3>
              <p className="text-sm text-gray-700">Endpoint <code className="bg-white px-2 py-1 rounded">GET /vehiculos/{placa}/tarifa</code> garantiza respuesta en ≤ 2000ms</p>
            </div>
            <div className="bg-primary-light border border-primary p-4 rounded-lg">
              <h3 className="font-semibold text-primary mb-2">⚡ Caché en Memoria</h3>
              <p className="text-sm text-gray-700">Tarifas precargadas al inicio (O(1)). Índices compuestos en BD: <code className="bg-white px-2 py-1 rounded">idx_placa_estado</code></p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}