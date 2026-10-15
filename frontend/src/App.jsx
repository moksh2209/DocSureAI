import { useState } from 'react'
import Scanner from './components/Scanner'
import Processing from './components/Processing'
import Results from './components/Results'
import About from './components/About'
import './index.css'

function App() {
  const [currentView, setCurrentView] = useState('scanner'); // scanner, processing, results, about
  const [file, setFile] = useState(null);
  const [resultsData, setResultsData] = useState(null);
  const [error, setError] = useState(null);

  const handleProcess = async (selectedFile) => {
    setFile(selectedFile);
    setCurrentView('processing');
    setError(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const apiUrl = import.meta.env.VITE_API_BASE_URL || '';
      const response = await fetch(`${apiUrl}/api/process`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to process document');
      }

      setResultsData(data);
      setCurrentView('results');
    } catch (err) {
      setError(err.message);
      setCurrentView('scanner');
    }
  };

  const handleReset = () => {
    setFile(null);
    setResultsData(null);
    setCurrentView('scanner');
    setError(null);
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="logo">DOCSUREAI</div>
        <nav className="main-nav">
          <button 
            className={`nav-btn ${currentView !== 'about' ? 'active' : ''}`}
            onClick={() => currentView === 'results' && resultsData ? setCurrentView('results') : setCurrentView('scanner')}
          >
            Scanner
          </button>
          <button 
            className={`nav-btn ${currentView === 'about' ? 'active' : ''}`}
            onClick={() => setCurrentView('about')}
          >
            About
          </button>
        </nav>
        <div className="privacy-badge">Privacy Protected</div>
      </header>

      <main className="main-content">
        {error && <div className="error-message">Error: {error}</div>}
        
        {currentView === 'scanner' && (
          <Scanner onProcess={handleProcess} />
        )}
        
        {currentView === 'processing' && (
          <Processing />
        )}
        
        {currentView === 'results' && resultsData && (
          <Results data={resultsData} onReset={handleReset} />
        )}

        {currentView === 'about' && (
          <About />
        )}
      </main>
    </div>
  )
}

export default App
