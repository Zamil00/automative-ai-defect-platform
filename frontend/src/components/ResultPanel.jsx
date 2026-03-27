import { FILE_BASE } from '../api/client'

const prettyMetric = (key) => key.replaceAll('_', ' ')

export default function ResultPanel({ result }) {
  if (!result) return null

  return (
    <section className="panel result-layout">
      <div>
        <div className="section-header compact">
          <div>
            <p className="eyebrow">Latest inference</p>
            <h2>{result.predicted_label}</h2>
          </div>
          <span className={`risk-pill ${result.risk_level}`}>{result.risk_level} risk</span>
        </div>

        <div className="info-grid">
          <div className="info-card"><span>Confidence</span><strong>{(result.confidence * 100).toFixed(1)}%</strong></div>
          <div className="info-card"><span>Review required</span><strong>{result.needs_manual_review ? 'Yes' : 'No'}</strong></div>
          <div className="info-card"><span>Model version</span><strong>{result.model_version}</strong></div>
          <div className="info-card"><span>Status</span><strong>{result.reviewer_status}</strong></div>
        </div>

        <p className="summary-text">{result.summary}</p>

        <div className="metrics-grid">
          {Object.entries(result.metrics).map(([key, value]) => (
            <div key={key} className="mini-metric">
              <span>{prettyMetric(key)}</span>
              <strong>{typeof value === 'number' ? value : String(value)}</strong>
            </div>
          ))}
        </div>
      </div>

      <div className="image-grid">
        <figure>
          <figcaption>Original upload</figcaption>
          <img src={`${FILE_BASE}${result.original_image_path}`} alt="Original upload" />
        </figure>

        <figure>
          <figcaption>Localized defect overlay</figcaption>
          <img src={`${FILE_BASE}${result.overlay_image_path}`} alt="Localized defect overlay" />
        </figure>

        <figure>
          <figcaption>Defect mask</figcaption>
          <img src={`${FILE_BASE}${result.mask_image_path}`} alt="Defect mask" />
        </figure>
      </div>
    </section>
  )
}