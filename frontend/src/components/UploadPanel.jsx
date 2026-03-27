import { useState } from 'react'

export default function UploadPanel({ onUpload }) {
  const [file, setFile] = useState(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  const submit = async (event) => {
    event.preventDefault()
    if (!file) {
      setError('Please select an image file first.')
      return
    }
    setBusy(true)
    setError('')
    try {
      await onUpload(file)
      setFile(null)
      event.target.reset()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="panel">
      <div className="section-header">
        <div>
          <p className="eyebrow">Inspection workflow</p>
          <h2>Upload automotive surface image</h2>
        </div>
      </div>
      <form className="upload-form" onSubmit={submit}>
        <input
          type="file"
          accept=".png,.jpg,.jpeg,.bmp,.webp"
          onChange={(event) => setFile(event.target.files?.[0] || null)}
        />
        <button disabled={busy} type="submit">
          {busy ? 'Analyzing...' : 'Run analysis'}
        </button>
      </form>
      {error ? <p className="error-text">{error}</p> : null}
    </section>
  )
}
