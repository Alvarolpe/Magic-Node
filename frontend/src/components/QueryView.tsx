import { useState } from 'react'

interface QueryResult {
  name: string
  creation_date: string
  author: string
  type: string
}

function QueryView() {
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [usersMentioned, setUsersMentioned] = useState('')
  const [reunionResult, setReunionResult] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [results, setResults] = useState<QueryResult[]>([])
  const [error, setError] = useState('')

  const handleQuery = async () => {
    setIsLoading(true)
    setError('')
    setResults([])

    try {
      // Build query parameters
      const params = new URLSearchParams()
      if (startDate) params.append('start_date', startDate)
      if (endDate) params.append('end_date', endDate)
      if (usersMentioned) params.append('users_mentioned', usersMentioned)
      if (reunionResult) params.append('reunion_result', reunionResult)

      const response = await fetch(`http://localhost:5004/query?${params.toString()}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        throw new Error(`Query failed: ${response.statusText}`)
      }

      const data = await response.json()
      
      if (data.status === 'success') {
        setResults(data.data)
      } else {
        throw new Error(data.detail || 'Unknown error occurred')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to query documents')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div>
      <h2 style={{ marginBottom: '1.5rem' }}>Query Documents</h2>
      
      <div className="filter-section">
        <div className="form-group">
          <label htmlFor="startDate">Start Date</label>
          <input
            id="startDate"
            type="date"
            value={startDate}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setStartDate(e.target.value)}
          />
        </div>

        <div className="form-group">
          <label htmlFor="endDate">End Date</label>
          <input
            id="endDate"
            type="date"
            value={endDate}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setEndDate(e.target.value)}
          />
        </div>

        <div className="form-group">
          <label htmlFor="users">Users Mentioned</label>
          <input
            id="users"
            type="text"
            value={usersMentioned}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setUsersMentioned(e.target.value)}
            placeholder="user1,user2"
          />
        </div>

        <div className="form-group">
          <label htmlFor="result">Reunion Result</label>
          <select
            id="result"
            value={reunionResult}
            onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setReunionResult(e.target.value)}
          >
            <option value="">All</option>
            <option value="completed">Completed</option>
            <option value="pending">Pending</option>
            <option value="in_progress">In Progress</option>
          </select>
        </div>
      </div>

      <button 
        className="btn btn-primary" 
        onClick={handleQuery}
        disabled={isLoading}
      >
        {isLoading ? 'Querying...' : 'Run Query'}
      </button>

      {error && <div className="error">{error}</div>}

      {results.length > 0 && (
        <div className="results">
          <h3 style={{ marginBottom: '1rem', marginTop: '1.5rem' }}>Query Results ({results.length})</h3>
          
          {results.map((result, index) => (
            <div key={index} className="result-item">
              <div className="result-header">
                <span className="result-title">{result.name}</span>
                <span className={`badge badge-${result.type.toLowerCase()}`}>
                  {result.type}
                </span>
              </div>
              <div className="result-meta">
                <div>Created: {result.creation_date}</div>
                <div>Author: {result.author}</div>
              </div>
            </div>
          ))}
        </div>
      )}

      {results.length === 0 && !isLoading && !error && (
        <div style={{ marginTop: '1.5rem', color: '#666' }}>
          No results found. Try different filters or run a query without filters.
        </div>
      )}
    </div>
  )
}

export default QueryView
