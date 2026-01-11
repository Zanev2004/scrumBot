import React, { useState } from 'react';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  // Handle file selection
  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setError(null);
  };

  // Upload and process CSV
  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('http://localhost:5000/api/process-csv', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (data.success) {
        setResults(data);
      } else {
        setError(data.message || 'Processing failed');
      }
    } catch (err) {
      setError('Failed to connect to server. Is Flask running?');
    } finally {
      setLoading(false);
    }
  };

  // Get color for risk level
  const getRiskColor = (level) => {
    switch (level) {
      case 'CRITICAL': return '#dc3545';
      case 'HIGH': return '#fd7e14';
      case 'MEDIUM': return '#ffc107';
      case 'LOW': return '#28a745';
      default: return '#6c757d';
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🤖 Scrumbot - Software Asset Management</h1>
        <p>AI-powered EOS tracking & risk assessment</p>
      </header>

      <div className="container">
        {/* Upload Section */}
        <div className="upload-section">
          <h2>Upload Software Inventory</h2>
          <input
            type="file"
            accept=".csv"
            onChange={handleFileChange}
            disabled={loading}
          />
          <button onClick={handleUpload} disabled={loading || !file}>
            {loading ? 'Processing...' : 'Analyze CSV'}
          </button>
          {error && <div className="error">{error}</div>}
        </div>

        {/* Loading Spinner */}
        {loading && (
          <div className="loading">
            <div className="spinner"></div>
            <p>Normalizing software names and calculating risk...</p>
          </div>
        )}

        {/* Results Section */}
        {results && !loading && (
          <>
            {/* Summary Dashboard */}
            <div className="summary">
              <h2>Risk Summary</h2>
              <div className="summary-cards">
                <div className="card critical">
                  <div className="number">{results.summary.critical}</div>
                  <div className="label">CRITICAL</div>
                </div>
                <div className="card high">
                  <div className="number">{results.summary.high}</div>
                  <div className="label">HIGH</div>
                </div>
                <div className="card medium">
                  <div className="number">{results.summary.medium}</div>
                  <div className="label">MEDIUM</div>
                </div>
                <div className="card low">
                  <div className="number">{results.summary.low}</div>
                  <div className="label">LOW</div>
                </div>
                <div className="card unknown">
                  <div className="number">{results.summary.unknown}</div>
                  <div className="label">UNKNOWN</div>
                </div>
              </div>
            </div>

            {/* Results Table */}
            <div className="results">
              <h2>Detailed Results ({results.summary.total} items)</h2>
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>Raw Input</th>
                      <th>Vendor</th>
                      <th>Product</th>
                      <th>Version</th>
                      <th>EOS Date</th>
                      <th>Risk Level</th>
                      <th>Days Until EOS</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.results.map((item, index) => (
                      <tr key={index}>
                        <td>{item.raw_input}</td>
                        <td>{item.vendor || 'N/A'}</td>
                        <td>{item.product || 'N/A'}</td>
                        <td>{item.version || 'N/A'}</td>
                        <td>{item.eos_date || 'N/A'}</td>
                        <td>
                          <span
                            className="risk-badge"
                            style={{ backgroundColor: getRiskColor(item.risk_level) }}
                          >
                            {item.risk_level}
                          </span>
                        </td>
                        <td>{item.days_until_eos !== null ? item.days_until_eos : 'N/A'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default App;