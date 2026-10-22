import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import RegistroEntrada from './pages/RegistroEntrada'
import RegistroSalida from './pages/RegistroSalida'
import ConsultaTarifa from './pages/ConsultaTarifa'
import ArqueoCaja from './pages/ArqueoCaja'
import Tarifas from './pages/Tarifas'
import Login from './pages/Login'

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route element={<Layout />}>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="entrada" element={<RegistroEntrada />} />
        <Route path="salida" element={<RegistroSalida />} />
        <Route path="tarifa/:placa?" element={<ConsultaTarifa />} />
        <Route path="arqueo" element={<ArqueoCaja />} />
        <Route path="tarifas" element={<Tarifas />} />
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}

export default App