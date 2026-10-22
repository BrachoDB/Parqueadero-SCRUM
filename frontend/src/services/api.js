import axios from 'axios'

const API_BASE_URL = '/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  },
  timeout: 10000
})

api.interceptors.response.use(
  response => response,
  error => {
    if (error.response) {
      return Promise.reject({
        status: error.response.status,
        message: error.response.data?.detail || error.message,
        data: error.response.data
      })
    } else if (error.request) {
      return Promise.reject({
        status: 0,
        message: 'No se pudo conectar al servidor. Verifique que el backend esté corriendo.',
        data: null
      })
    } else {
      return Promise.reject({
        status: -1,
        message: error.message,
        data: null
      })
    }
  }
)

export const vehiculosApi = {
  registrarEntrada: (data) =>
    api.post('/vehiculos/entrada', data),

  consultarTarifa: (placa) =>
    api.get(`/vehiculos/${encodeURIComponent(placa)}/tarifa`),

  registrarSalida: (data) =>
    api.post('/vehiculos/salida', data),

  getActivos: () =>
    api.get('/vehiculos/activos')
}

export const tarifasApi = {
  listar: () =>
    api.get('/tarifas')
}

export const reportesApi = {
  arqueoCaja: (fecha) => {
    const params = fecha ? { fecha } : {}
    return api.get('/reportes/arqueo', { params })
  }
}

export const systemApi = {
  healthCheck: () =>
    api.get('/health')
}

export default api