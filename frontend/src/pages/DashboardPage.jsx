import { useEffect, useState } from 'react'
import { fetchDashboard, fetchInspections, reviewInspection, uploadInspection } from '../api/client'
import MetricCard from '../components/MetricCard'
import UploadPanel from '../components/UploadPanel'
import ResultPanel from '../components/ResultPanel'
import InspectionTable from '../components/InspectionTable'

export default function DashboardPage() {
  const [dashboard, setDashboard] = useState(null)
  const [inspections, setInspections] = useState([])
  const [latestResult, setLatestResult] = useState(null)
  const [loading, setLoading] = useState(true)
  const [globalError, setGlobalError] = useState('')

  const load = async () => {
    setLoading(true)
    setGlobalError('')
    try {
      const [dashboardData, inspectionData] = await Promise.all([
        fetchDashboard(),
        fetchInspections(),
      ])
      setDashboard(dashboardData)
      setInspections(inspectionData)
    } catch (err) {
      setGlobalError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  const handleUpload = async (file) => {
    const result = await uploadInspection(file)
    setLatestResult(result)
    await load()
  }

  const handleReview = async (id, payload) => {
    await reviewInspection(id, payload)
    await load()
  }

  return (
    <main className="page-shell">
      <section className="hero">
        <div>
          <p className="eyebrow">Automotive AI Engineering Demo</p>
          <h1>ARRK AI Visual Defect Platform</h1>
          <p className="lead">
            A more production-minded portfolio project with an ML/CV inference service, review workflow,
            PostgreSQL-ready persistence, and a React dashboard for explainable defect analysis.
          </p>
        </div>
        <div className="hero-grid">
          <MetricCard label="Total analyses" value={dashboard?.total_analyses ?? 0} hint="Persisted in database" />
          <MetricCard label="Review rate" value={`${((dashboard?.review_rate ?? 0) * 100).toFixed(1)}%`} hint="Queue pressure" />
          <MetricCard label="Avg. confidence" value={`${((dashboard?.average_confidence ?? 0) * 100).toFixed(1)}%`} hint="Model quality signal" />
          <MetricCard label="Approval rate" value={`${((dashboard?.approval_rate ?? 0) * 100).toFixed(1)}%`} hint="Human validation outcome" />
        </div>
      </section>

      <UploadPanel onUpload={handleUpload} />
      {latestResult ? <ResultPanel result={latestResult} /> : null}

      {globalError ? <p className="error-text">{globalError}</p> : null}
      {loading ? <p className="loading-text">Loading dashboard...</p> : null}
      <InspectionTable inspections={inspections} onReview={handleReview} />
    </main>
  )
}
