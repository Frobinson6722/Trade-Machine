import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import TradesPage from './pages/TradesPage'
import AgentsPage from './pages/AgentsPage'
import LearningPage from './pages/LearningPage'
import SettingsPage from './pages/SettingsPage'

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/trades" element={<TradesPage />} />
        <Route path="/agents" element={<AgentsPage />} />
        <Route path="/learning" element={<LearningPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Routes>
    </Layout>
  )
}
