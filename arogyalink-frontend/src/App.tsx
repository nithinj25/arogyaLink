import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import LandingPage from './pages/LandingPage'
import Dashboard from './pages/Dashboard'
import FamiliesPage from './pages/FamiliesPage'
import RegisterFamilyPage from './pages/RegisterFamilyPage'
import FamilyDetailPage from './pages/FamilyDetailPage'
import CasesPage from './pages/CasesPage'
import CaseDetailPage from './pages/CaseDetailPage'
import AshaPage from './pages/AshaPage'

function AdminApp() {
  return (
    <Layout>
      <Routes>
        <Route index element={<Dashboard />} />
        <Route path="families" element={<FamiliesPage />} />
        <Route path="families/new" element={<RegisterFamilyPage />} />
        <Route path="families/:phone" element={<FamilyDetailPage />} />
        <Route path="cases" element={<CasesPage />} />
        <Route path="cases/:id" element={<CaseDetailPage />} />
        <Route path="*" element={<Navigate to="" replace />} />
      </Routes>
    </Layout>
  )
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/admin/*" element={<AdminApp />} />
      <Route path="/asha" element={<AshaPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
