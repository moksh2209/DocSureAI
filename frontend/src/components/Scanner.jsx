import { useState, useRef } from 'react'

const ACCEPTED_TYPES = ['image/jpeg', 'image/jpg', 'image/png']

function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1048576).toFixed(1) + ' MB'
}

export default function Scanner({ onProcess }) {
  const [file, setFile] = useState(null)
  const [dragging, setDragging] = useState(false)
  const fileInputRef = useRef(null)

  const handleFile = (f) => {
    if (f && ACCEPTED_TYPES.includes(f.type)) {
      setFile(f)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragging(false)
    if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0])
  }

  const handleDragOver = (e) => { e.preventDefault(); e.stopPropagation(); setDragging(true) }
  const handleDragLeave = (e) => { e.preventDefault(); e.stopPropagation(); setDragging(false) }

  return (
    <div className="scanner-page">
      <div className="scanner-hero">
        <h1>Scan. Understand. Protect.</h1>
        <p>Transform document images into clean, structured information while automatically identifying and redacting sensitive data.</p>
      </div>

      <div className="scanner-grid">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {/* Drop Zone */}
          <div
            className={`drop-zone${dragging ? ' dragging' : ''}`}
            onClick={() => fileInputRef.current?.click()}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
          >
            <div className="drop-zone-icon">
              <svg width="32" height="32" fill="none" stroke="currentColor" strokeWidth="1.8" viewBox="0 0 24 24">
                <path d="M3 7V5a2 2 0 012-2h2m10 0h2a2 2 0 012 2v2m0 10v2a2 2 0 01-2 2h-2m-10 0H5a2 2 0 01-2-2v-2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M9 12h6m-6 3h4m-5-6h7a1 1 0 011 1v7a1 1 0 01-1 1H8a1 1 0 01-1-1v-7a1 1 0 011-1z" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <h2>Upload your document</h2>
            <p className="hint">Drag & drop your document here</p>
            <span className="or-text">or</span>
            <label className="browse-btn" onClick={(e) => e.stopPropagation()}>
              <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              <span>Browse files</span>
              <input
                ref={fileInputRef}
                type="file"
                accept=".jpg,.jpeg,.png"
                style={{ display: 'none' }}
                onChange={(e) => { if (e.target.files[0]) handleFile(e.target.files[0]) }}
              />
            </label>
            <div className="supported-formats">
              <span>Supported formats: JPG, JPEG, PNG</span>
            </div>
          </div>

          {/* File Preview Card */}
          {file && (
            <div className="file-preview-card">
              <div className="file-info">
                <div className="file-icon">
                  <svg width="24" height="24" fill="none" stroke="currentColor" strokeWidth="1.8" viewBox="0 0 24 24">
                    <path d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
                <div className="file-details">
                  <div className="file-name-row">
                    <span className="file-name">{file.name}</span>
                    <span className="ready-badge">
                      <svg width="12" height="12" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"/>
                      </svg>
                      Ready to process
                    </span>
                  </div>
                  <span className="file-size">{formatSize(file.size)}</span>
                </div>
              </div>
              <div className="file-actions">
                <button className="remove-btn" onClick={() => setFile(null)} aria-label="Remove document">
                  <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                    <path d="M6 18L18 6M6 6l12 12" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </button>
                <button className="process-btn" onClick={() => onProcess(file)}>
                  <span>Process Document</span>
                  <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                    <path d="M14 5l7 7m0 0l-7 7m7-7H3" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </button>
              </div>
            </div>
          )}

          {/* Privacy Notice */}
          <div className="privacy-notice">
            <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            <p>Your document is processed locally on this device. Generated results are stored locally.</p>
          </div>
        </div>

        {/* Info Sidebar */}
        <div className="info-sidebar">
          <div className="info-sidebar-header">
            <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" style={{ color: 'var(--primary-container)' }}>
              <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            <h3>DOCUMENT PROCESSING</h3>
          </div>
          <ul className="info-list">
            <li>
              <div className="info-check">
                <svg width="12" height="12" fill="none" stroke="currentColor" strokeWidth="3" viewBox="0 0 24 24">
                  <path d="M5 13l4 4L19 7" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <div>
                <strong>Computer vision + OCR</strong>
                <span>Pixel preprocessing and spatial text recognition across document contents.</span>
              </div>
            </li>
            <li>
              <div className="info-check">
                <svg width="12" height="12" fill="none" stroke="currentColor" strokeWidth="3" viewBox="0 0 24 24">
                  <path d="M5 13l4 4L19 7" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <div>
                <strong>Document quality analysis</strong>
                <span>Automated contrast assessment, angle deskewing, and layout validation.</span>
              </div>
            </li>
            <li>
              <div className="info-check">
                <svg width="12" height="12" fill="none" stroke="currentColor" strokeWidth="3" viewBox="0 0 24 24">
                  <path d="M5 13l4 4L19 7" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <div>
                <strong>Sensitive information detection</strong>
                <span>Pattern and text analysis to detect personal identifiers and credentials.</span>
              </div>
            </li>
            <li>
              <div className="info-check">
                <svg width="12" height="12" fill="none" stroke="currentColor" strokeWidth="3" viewBox="0 0 24 24">
                  <path d="M5 13l4 4L19 7" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <div>
                <strong>Visual redaction</strong>
                <span>Permanent overlay masking applied directly to document image regions.</span>
              </div>
            </li>
          </ul>
        </div>
      </div>

      <div className="tech-strip">
        <div className="tech-strip-inner">
          Powered by <strong>&nbsp;Python</strong>&nbsp;·&nbsp;<strong>OpenCV</strong>&nbsp;·&nbsp;<strong>NumPy</strong>&nbsp;·&nbsp;<strong>EasyOCR</strong>&nbsp;·&nbsp;<strong>PyTorch</strong>&nbsp;·&nbsp;<strong>Torchvision</strong>
        </div>
      </div>
    </div>
  )
}
