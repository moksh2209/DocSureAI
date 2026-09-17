const STAGES = [
  { num: '01', name: 'Image Preprocessing', desc: 'Normalizes color channels, contrast, and removes high-frequency capture noise.' },
  { num: '02', name: 'Document Boundary Detection', desc: 'Isolates document contours from background surfaces using edge gradient analysis.' },
  { num: '03', name: 'Perspective Correction', desc: 'Applies homographic rectification to flatten angled scans and eliminate skew distortion.' },
  { num: '04', name: 'Image Enhancement', desc: 'Applies adaptive binarization, de-shadowing, and sharpening for optimal text clarity.' },
  { num: '05', name: 'Document Quality Assessment', desc: 'Evaluates resolution threshold, sharpness index, and illumination variance.' },
  { num: '06', name: 'Optical Character Recognition', desc: 'Extracts alphanumeric glyphs, text bounding boxes, and positional coordinates.' },
  { num: '07', name: 'OCR Result Analysis', desc: 'Validates character confidence distributions, lexical integrity, and reading flow.' },
  { num: '08', name: 'Document Structure Analysis', desc: 'Classifies hierarchical sections, tabular entities, key-value pairs, and labels.' },
  { num: '09', name: 'Sensitive Information Detection', desc: 'Detects personal identifiers, national IDs, financial records, and confidential data.' },
  { num: '10', name: 'Visual Redaction', desc: 'Applies irreversible bounding mask redactions to target sensitive visual regions.' },
]

export default function Processing() {
  // The backend runs the entire pipeline as one request.
  // We show all stages as "Processing" to honestly reflect that the pipeline is running.
  return (
    <div className="processing-page">
      <div className="processing-header-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '1.5rem', flexWrap: 'wrap' }}>
          <div>
            <h1>Processing your document</h1>
            <p className="subtitle">Running local computer vision and OCR pipeline</p>
          </div>
        </div>
        <div className="processing-progress">
          <div className="progress-label">
            <span>Pipeline Running</span>
            <span className="progress-pct" style={{ animation: 'pulse-dot 1.5s ease-in-out infinite' }}>Processing...</span>
          </div>
          <div className="progress-bar">
            <div className="progress-bar-fill" style={{ width: '100%', animation: 'indeterminate 1.5s ease-in-out infinite' }} />
          </div>
          <style>{`
            @keyframes indeterminate {
              0% { width: 10%; margin-left: 0; }
              50% { width: 60%; margin-left: 20%; }
              100% { width: 10%; margin-left: 90%; }
            }
          `}</style>
        </div>
      </div>

      <div className="pipeline-card">
        <div className="pipeline-card-header">
          <h2>Pipeline Stages</h2>
          <span>10 stages total</span>
        </div>
        <div className="stage-list">
          {STAGES.map((stage) => (
            <div key={stage.num} className="stage-item active">
              <div className="stage-left">
                <span className="stage-num">{stage.num}</span>
                <div className="stage-info">
                  <h3>{stage.name}</h3>
                  <p>{stage.desc}</p>
                </div>
              </div>
              <span className="badge badge-processing">
                <svg className="spinner" fill="none" viewBox="0 0 24 24">
                  <circle style={{ opacity: 0.25 }} cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path style={{ opacity: 0.75 }} fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
                </svg>
                Processing
              </span>
            </div>
          ))}
        </div>
      </div>

      <div className="privacy-notice">
        <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
          <rect height="11" rx="2" ry="2" width="18" x="3" y="11" />
          <path d="M7 11V7a5 5 0 0 1 10 0v4" />
        </svg>
        <p>Your document is processed locally on this device. Generated results are stored locally.</p>
      </div>
    </div>
  )
}
