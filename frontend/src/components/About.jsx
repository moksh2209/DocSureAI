const STAGES = [
  'Image Preprocessing',
  'Document Boundary Detection',
  'Perspective Correction',
  'Image Enhancement',
  'Document Quality Assessment',
  'Optical Character Recognition',
  'OCR Result Analysis',
  'Document Structure Analysis',
  'Sensitive Information Detection',
  'Visual Redaction',
]

const TECHNOLOGIES = [
  'Python', 'OpenCV', 'NumPy', 'EasyOCR', 'PyTorch', 'Torchvision', 'React', 'FastAPI'
]

export default function About() {
  return (
    <div className="about-page">
      <div className="about-hero">
        <h1>About DocSureAI</h1>
        <p>
          DocSureAI is a computer-vision and OCR based document processing application that transforms document images into structured information while automatically detecting and visually redacting sensitive information.
        </p>
      </div>

      {/* Pipeline */}
      <div className="about-card">
        <h2>Processing Pipeline</h2>
        <div className="pipeline-stages">
          {STAGES.map((name, i) => (
            <div key={i} className="pipeline-stage">
              <span className="pipeline-stage-num">{String(i + 1).padStart(2, '0')}</span>
              <span className="pipeline-stage-name">{name}</span>
            </div>
          ))}
        </div>
        <p style={{ fontSize: 13, color: 'var(--on-surface-variant)', marginTop: '1rem', lineHeight: 1.6 }}>
          Step 2 (Document Boundary Detection) includes a full-image fallback for images where a document contour cannot be detected, such as pre-cropped digital images.
        </p>
      </div>

      {/* Technologies */}
      <div className="about-card">
        <h2>Technologies</h2>
        <div className="tech-grid">
          {TECHNOLOGIES.map((tech) => (
            <div key={tech} className="tech-item">{tech}</div>
          ))}
        </div>
      </div>

      {/* Privacy */}
      <div className="about-card">
        <h2>Privacy & Security</h2>
        <div className="about-privacy">
          <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
            <path d="m9 12 2 2 4-4" />
          </svg>
          <div>
            <p>Your document is processed locally on this device. Generated results are stored locally.</p>
            <ul style={{ marginTop: 8, paddingLeft: 20, fontSize: 14, color: 'var(--on-surface-variant)', lineHeight: 1.8 }}>
              <li>Sensitive information is detected using OCR text and pattern matching.</li>
              <li>Visual redaction uses solid black rectangles applied permanently to the image.</li>
              <li>Original source images are preserved separately.</li>
              <li>Generated reports containing sensitive data remain local in the output directory.</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Limitations */}
      <div className="about-card">
        <h2>Known Limitations</h2>
        <ul style={{ paddingLeft: 20, fontSize: 14, color: 'var(--on-surface-variant)', lineHeight: 1.8 }}>
          <li>OCR can misread characters or punctuation.</li>
          <li>OCR errors can affect downstream pattern detection.</li>
          <li>URL detection is intentionally conservative.</li>
          <li>Pre-cropped digital images may use the full-image boundary fallback.</li>
        </ul>
      </div>
    </div>
  )
}
