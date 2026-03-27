const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000/api/v1'
const FILE_BASE = API_BASE.replace('/api/v1', '')

export { API_BASE, FILE_BASE }

export async function fetchDashboard() {
  const response = await fetch(`${API_BASE}/dashboard`)
  if (!response.ok) throw new Error('Failed to load dashboard data.')
  return response.json()
}

export async function fetchInspections() {
  const response = await fetch(`${API_BASE}/inspections`)
  if (!response.ok) throw new Error('Failed to load inspections.')
  return response.json()
}

export async function uploadInspection(file) {
  const formData = new FormData()
  formData.append('file', file)
  const response = await fetch(`${API_BASE}/inspections`, {
    method: 'POST',
    body: formData,
  })
  const data = await response.json()
  if (!response.ok) throw new Error(data.detail || 'Upload failed.')
  return data
}

export async function reviewInspection(id, payload) {
  const response = await fetch(`${API_BASE}/inspections/${id}/review`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  const data = await response.json()
  if (!response.ok) throw new Error(data.detail || 'Review update failed.')
  return data
}
