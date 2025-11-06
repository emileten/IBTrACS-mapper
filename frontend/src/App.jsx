import { useState } from 'react'
import Map from './Map'
import MonthSelector from './MonthSelector'

function App() {
  // Initialize with current month (format: YYYY-MM)
  const [selectedMonth, setSelectedMonth] = useState(() => {
    const now = new Date()
    const year = now.getFullYear()
    const month = String(now.getMonth() + 1).padStart(2, '0')
    return `${year}-${month}`
  })

  // State for storms data, loading, and errors
  const [storms, setStorms] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // Fetch storms data manually (called when Plot button is clicked)
  const fetchStorms = async () => {
    // Convert YYYY-MM to YYYY/MM for API
    const [year, month] = selectedMonth.split('-')
    
    // Use environment variable for API URL, fallback to proxy path for development
    const apiBaseUrl = import.meta.env.VITE_BACKEND_API_URL
    const apiUrl = apiBaseUrl 
      ? `${apiBaseUrl}/storms/${year}/${month}`
      : `/api/storms/${year}/${month}`

    setLoading(true)
    setError(null)

    try {
      const response = await fetch(apiUrl)
      if (!response.ok) {
        throw new Error(`Failed to fetch data: ${response.statusText}`)
      }
      const data = await response.json()
      setStorms(data.storms || [])
      if (!data.storms || data.storms.length === 0) {
        setError('No storms found for this month')
      }
    } catch (err) {
      setError(err.message)
      setStorms([])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <MonthSelector
        value={selectedMonth}
        onChange={setSelectedMonth}
        onPlot={fetchStorms}
      />
      {loading && (
        <div className="status-message loading">
          Loading storms data...
        </div>
      )}
      {error && (
        <div className="status-message error">
          Error: {error}
        </div>
      )}
      {!loading && !error && storms.length > 0 && (
        <div className="status-message success">
          Found {storms.length} storm{storms.length !== 1 ? 's' : ''}
        </div>
      )}
      <Map storms={storms} />
    </div>
  )
}

export default App

