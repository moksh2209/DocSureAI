const API_BASE = import.meta.env.VITE_API_BASE_URL;

export default function Results({ data, onReset }) {
  const { filename, quality, ocr, structure, sensitive_data, redaction, images } = data

  // Extract metric values
  const qualityScore = quality?.overall_score ?? quality?.quality_score ?? '—'
  const ocrConfidence = ocr?.confidence ?? '—'

  const sensitiveItems = sensitive_data?.detections?.length ?? sensitive_data?.total_detections ?? 0
  const redactedRegions = redaction?.regions_redacted ?? redaction?.total_regions ?? 0

  // Extracted text
  const extractedText = ocr?.results?.results?.[0]?.extracted_text || ocr?.analysis?.best_candidate?.extracted_text || ''

  // Structure
  const stats = structure?.statistics || {}
  const docTitle = structure?.document_title || '(not detected)'

  // Sensitive items table
  const detections = sensitive_data?.detections || []

  return (
    <div className="results-page">
      {/* Header */}
      <div className="results-header">
        <h1>Document Analysis</h1>
        <p className="results-sub">
          Analysis complete for <code className="results-filename">{filename}</code>
        </p>

        {/* Success Panel */}
        <div className="success-panel">
          <div className="success-info">
            <div className="success-icon">
              <svg width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2.2" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                <path d="m9 12 2 2 4-4" />
              </svg>
            </div>
            <div className="success-text">
              <h2>Sensitive information protected</h2>
              <p>{sensitiveItems} sensitive items detected · {redactedRegions} unique regions redacted</p>
            </div>
          </div>
          <div className="success-actions">
            <button className="btn-outline" onClick={() => {
              const el = document.getElementById('sensitive-section')
              if (el) el.scrollIntoView({ behavior: 'smooth' })
            }}>
              <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <polyline points="14 2 14 8 20 8" />
              </svg>
              View Detection Report
            </button>
            <button className="btn-primary" onClick={() => {
              const el = document.getElementById('comparison-section')
              if (el) el.scrollIntoView({ behavior: 'smooth' })
            }}>
              <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round">
                <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z" />
                <circle cx="12" cy="12" r="3" />
              </svg>
              View Redacted Document
            </button>
          </div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="metrics-grid">
        {/* Quality */}
        <div className="metric-card">
          <div className="metric-header">
            <span className="metric-label">Document Quality</span>
            <div className="metric-icon" style={{ background: 'var(--surface-container-low)', color: 'var(--primary-container)' }}>
              <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10" />
                <path d="m14 10-4 4" /><path d="m10 10 4 4" />
              </svg>
            </div>
          </div>
          <div className="metric-value">
            <span className="big">{typeof qualityScore === 'number' ? qualityScore.toFixed(2) : qualityScore}</span>
            <span className="unit">/ 100</span>
          </div>
          <div className="metric-bar">
            <div className="metric-bar-track">
              <div className="metric-bar-fill" style={{ width: `${typeof qualityScore === 'number' ? qualityScore : 0}%`, background: 'var(--primary-container)' }} />
            </div>
          </div>
        </div>

        {/* OCR Confidence */}
        <div className="metric-card">
          <div className="metric-header">
            <span className="metric-label">OCR Confidence</span>
            <div className="metric-icon" style={{ background: 'var(--surface-container-low)', color: 'var(--secondary)' }}>
              <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round">
                <path d="M4 7V4h3" /><path d="M20 7V4h-3" /><path d="M4 17v3h3" /><path d="M20 17v3h-3" />
                <line x1="9" x2="15" y1="12" y2="12" />
              </svg>
            </div>
          </div>
          <div className="metric-value">
            <span className="big">{typeof ocrConfidence === 'number' ? ocrConfidence.toFixed(2) : ocrConfidence}</span>
            <span className="unit">%</span>
          </div>
          <div className="metric-bar">
            <div className="metric-bar-track">
              <div className="metric-bar-fill" style={{ width: `${typeof ocrConfidence === 'number' ? ocrConfidence : 0}%`, background: 'var(--secondary)' }} />
            </div>
          </div>
        </div>

        {/* Sensitive Items */}
        <div className="metric-card">
          <div className="metric-header">
            <span className="metric-label">Sensitive Items</span>
            <div className="metric-icon" style={{ background: 'rgba(255,218,214,0.5)', color: 'var(--error)' }}>
              <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                <line x1="12" x2="12" y1="8" y2="12" /><line x1="12" x2="12.01" y1="16" y2="16" />
              </svg>
            </div>
          </div>
          <div className="metric-value">
            <span className="big">{sensitiveItems}</span>
            {sensitiveItems > 0 && (
              <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.04em', fontWeight: 700, color: 'var(--on-error-container)', background: 'var(--error-container)', padding: '2px 8px', borderRadius: 4 }}>
                Detected
              </span>
            )}
          </div>
          <div className="metric-bar">
            <div className="metric-bar-track">
              <div className="metric-bar-fill" style={{ width: sensitiveItems > 0 ? '100%' : '0%', background: 'var(--error)' }} />
            </div>
          </div>
        </div>

        {/* Redacted Regions */}
        <div className="metric-card">
          <div className="metric-header">
            <span className="metric-label">Redacted Regions</span>
            <div className="metric-icon" style={{ background: 'var(--inverse-surface)', color: 'var(--inverse-on-surface)' }}>
              <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round">
                <rect height="11" rx="2" ry="2" width="18" x="3" y="11" />
                <path d="M7 11V7a5 5 0 0 1 10 0v4" />
              </svg>
            </div>
          </div>
          <div className="metric-value">
            <span className="big">{redactedRegions}</span>
            {redactedRegions > 0 && (
              <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.04em', fontWeight: 700, color: 'var(--on-secondary)', background: 'var(--secondary)', padding: '2px 10px', borderRadius: 4 }}>
                Protected
              </span>
            )}
          </div>
          <div className="metric-bar">
            <div className="metric-bar-track">
              <div className="metric-bar-fill" style={{ width: redactedRegions > 0 ? '100%' : '0%', background: 'var(--inverse-surface)' }} />
            </div>
          </div>
        </div>
      </div>

      {/* Document Comparison */}
      <div className="comparison-section" id="comparison-section">
        <div className="comparison-bar">
          <h2>Document Comparison</h2>
        </div>
        <div className="comparison-grid">
          {/* Original */}
          <div className="doc-panel">
            <div className="doc-panel-header">
              <div className="doc-panel-title">
                <div className="doc-panel-dot" style={{ background: '#f59e0b' }} />
                <span>ORIGINAL DOCUMENT</span>
              </div>
            </div>
            <div className="doc-panel-canvas">
              <img src={`${API_BASE}${images?.scanned || images?.original}`} alt="Original Document" onError={(e) => { e.target.style.display = 'none' }} />
            </div>
            <div className="doc-panel-footer">
              <span>Original resolution preview</span>
            </div>
          </div>

          {/* Redacted */}
          <div className="doc-panel">
            <div className="doc-panel-header">
              <div className="doc-panel-title">
                <div className="doc-panel-dot" style={{ background: 'var(--secondary)' }} />
                <span>REDACTED DOCUMENT</span>
              </div>
              <span className="doc-panel-badge" style={{ color: 'var(--secondary)', background: 'rgba(153,239,229,0.3)', border: '1px solid rgba(0,106,99,0.3)' }}>Solid Black Mask Applied</span>
            </div>
            <div className="doc-panel-canvas">
              <img src={`${API_BASE}${images?.redacted}`} alt="Redacted Document" onError={(e) => { e.target.style.display = 'none' }} />
            </div>
            <div className="doc-panel-footer">
              <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <span style={{ width: 12, height: 12, background: '#000', display: 'inline-block' }} />
                Redacted field
              </span>
              <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 11, fontWeight: 600, color: 'var(--secondary)' }}>Protected</span>
            </div>
          </div>
        </div>
      </div>

      {/* Sensitive Information Table */}
      {detections.length > 0 && (
        <div className="sensitive-section" id="sensitive-section">
          <div className="section-title-bar">
            <div className="section-title-icon">
              <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
              </svg>
            </div>
            <h2>Sensitive Information Detected</h2>
          </div>
          <div className="sensitive-table-card">
            <div style={{ overflowX: 'auto' }}>
              <table className="sensitive-table">
                <thead>
                  <tr>
                    <th>Type</th>
                    <th>Matched Text</th>
                    <th>Confidence</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {detections.map((d, i) => (
                    <tr key={i}>
                      <td className="type-cell">{d.type || d.category || '—'}</td>
                      <td className="text-cell">{d.matched_text || d.text || d.value || '—'}</td>
                      <td className="confidence-cell">{d.confidence != null ? `${(d.confidence * 100).toFixed(1)}%` : d.ocr_confidence != null ? `${d.ocr_confidence.toFixed(1)}%` : '—'}</td>
                      <td>
                        <span className="redacted-badge">
                          <svg width="12" height="12" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round">
                            <rect height="11" rx="2" ry="2" width="18" x="3" y="11" />
                            <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                          </svg>
                          Redacted
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Extracted Text & Document Structure */}
      <div className="text-structure-grid">
        {/* Extracted Text */}
        <div className="card-section">
          <div className="card-section-header">
            <div className="card-section-title">
              <div className="section-title-icon">
                <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="21" x2="3" y1="10" y2="10" /><line x1="21" x2="3" y1="6" y2="6" />
                  <line x1="21" x2="3" y1="14" y2="14" /><line x1="21" x2="3" y1="18" y2="18" />
                </svg>
              </div>
              <h3>Extracted Text</h3>
            </div>
            <div className="card-section-badges">
              {typeof ocrConfidence === 'number' && (
                <span className="info-badge info-badge-teal">OCR Confidence: {ocrConfidence.toFixed(2)}%</span>
              )}
            </div>
          </div>
          <div className="extracted-text-box">{extractedText || 'No text extracted.'}</div>
        </div>

        {/* Document Structure */}
        <div className="card-section">
          <div className="card-section-header">
            <div className="card-section-title">
              <div className="section-title-icon">
                <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round">
                  <rect height="7" width="7" x="3" y="3" /><rect height="7" width="7" x="14" y="3" />
                  <rect height="7" width="7" x="14" y="14" /><rect height="7" width="7" x="3" y="14" />
                </svg>
              </div>
              <h3>Document Structure</h3>
            </div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <div className="structure-title-card">
              <div className="label">Title</div>
              <div className="value">{docTitle}</div>
            </div>
            <div className="structure-grid">
              <div className="structure-stat">
                <div className="label">Sections</div>
                <div className="value">{stats.section_count ?? 0}</div>
              </div>
              <div className="structure-stat">
                <div className="label">Paragraphs</div>
                <div className="value">{stats.paragraph_count ?? 0}</div>
              </div>
              <div className="structure-stat">
                <div className="label">Bullet Lists</div>
                <div className="value">{stats.bullet_list_count ?? 0}</div>
              </div>
              <div className="structure-stat">
                <div className="label">Numbered Lists</div>
                <div className="value">{stats.numbered_list_count ?? 0}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* New Scan */}
      <div className="new-scan-bar">
        <button className="btn-primary" onClick={onReset} style={{ padding: '12px 28px', fontSize: 15 }}>
          <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="23 4 23 10 17 10" /><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
          </svg>
          Scan New Document
        </button>
      </div>
    </div>
  )
}
