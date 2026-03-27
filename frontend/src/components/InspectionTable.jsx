import { useState } from 'react'

export default function InspectionTable({ inspections, onReview }) {
  const [drafts, setDrafts] = useState({})

  const updateDraft = (id, field, value) => {
    setDrafts((current) => ({
      ...current,
      [id]: {
        reviewer_status: current[id]?.reviewer_status || 'approved',
        reviewed_by: current[id]?.reviewed_by || '',
        reviewer_note: current[id]?.reviewer_note || '',
        [field]: value,
      },
    }))
  }

  return (
    <section className="panel">
      <div className="section-header">
        <div>
          <p className="eyebrow">Validation queue</p>
          <h2>Recent inspections</h2>
        </div>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>File</th>
              <th>Prediction</th>
              <th>Confidence</th>
              <th>Risk</th>
              <th>Review</th>
              <th>Reviewer</th>
              <th>Note</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {inspections.map((item) => {
              const draft = drafts[item.id] || {
                reviewer_status: item.reviewer_status === 'pending' ? 'approved' : item.reviewer_status,
                reviewed_by: item.reviewed_by || '',
                reviewer_note: item.reviewer_note || '',
              }

              return (
                <tr key={item.id}>
                  <td>{item.filename}</td>
                  <td>{item.predicted_label}</td>
                  <td>{(item.confidence * 100).toFixed(1)}%</td>
                  <td><span className={`risk-pill ${item.risk_level}`}>{item.risk_level}</span></td>
                  <td>{item.reviewer_status}</td>
                  <td>
                    <input
                      className="table-input"
                      placeholder="Reviewer"
                      value={draft.reviewed_by}
                      onChange={(event) => updateDraft(item.id, 'reviewed_by', event.target.value)}
                    />
                  </td>
                  <td>
                    <input
                      className="table-input"
                      placeholder="Optional note"
                      value={draft.reviewer_note}
                      onChange={(event) => updateDraft(item.id, 'reviewer_note', event.target.value)}
                    />
                  </td>
                  <td>
                    <div className="action-stack">
                      <select
                        value={draft.reviewer_status}
                        onChange={(event) => updateDraft(item.id, 'reviewer_status', event.target.value)}
                      >
                        <option value="approved">approve</option>
                        <option value="rejected">reject</option>
                        <option value="pending">pending</option>
                      </select>
                      <button
                        className="secondary-button"
                        onClick={() => onReview(item.id, draft)}
                      >
                        Save
                      </button>
                    </div>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </section>
  )
}
