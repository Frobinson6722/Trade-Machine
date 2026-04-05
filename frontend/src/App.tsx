import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import AgentsPage from './pages/AgentsPage'
import MorePage from './pages/MorePage'
import { ActivityProvider } from './hooks/useActivityFeed'

export default function App() {
  return (
    <ActivityProvider>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/agents" element={<AgentsPage />} />
          <Route path="/more" element={<MorePage />} />
        </Routes>
      </Layout>
    </ActivityProvider>
  )
}
