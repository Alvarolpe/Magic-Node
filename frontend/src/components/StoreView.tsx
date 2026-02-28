import { useState, useEffect } from 'react'

interface FileMetadata {
  name: string
  contents: string[]
  creation_date: string
  extra: string
}

interface StoreViewProps {
  extractedData: FileMetadata[]
}

function StoreView({ extractedData }: StoreViewProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [success, setSuccess] = useState('')
  const [error, setError] = useState('')
  const [dataToStore, setDataToStore] = useState<FileMetadata[]>([])

  // Update data when extractedData changes
  useEffect(() => {
    if (extractedData.length > 0) {
      setDataToStore(extractedData)
    }
  }, [extractedData])

  const handleStore = async () => {
    if (dataToStore.length === 0) {
      setError('No data to store. Please extract metadata first.')
      return
    }

    setIsLoading(true)
    setError('')
    setSuccess('')

    try {
      const response = await fetch('http://localhost:5004/store', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(dataToStore),
      })

      if (!response.ok) {
        throw new Error(`Store failed: ${response.statusText}`)
      }

      const result = await response.json()
      
      if (result.status === 'success') {
        setSuccess(`Successfully stored ${dataToStore.length} documents metadata`)
      } else {
        throw new Error(result.detail || 'Unknown error occurred')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to store metadata')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div>
      <h2 style={{ marginBottom: '1.5rem' }}>Store Metadata to Database</h2>
      
      {dataToStore.length > 0 && (
        <div style={{ marginBottom: '1.5rem', padding: '1rem', backgroundColor: '#f5f5f5', borderRadius: '8px' }}>
          <strong>Ready to store:</strong> {dataToStore.length} documents
        </div>
      )}

      {dataToStore.length === 0 && (
        <div style={{ marginBottom: '1.5rem', padding: '1rem', backgroundColor: '#fff3cd', borderRadius: '8px' }}>
          No data available. Please go to "Extract Metadata" tab and extract metadata first.
        </div>
      )}

      <button 
        className="btn btn-primary" 
        onClick={handleStore}
        disabled={isLoading || dataToStore.length === 0}
      >
        {isLoading ? 'Storing...' : 'Store to Database'}
      </button>

      {error && <div className="error" style={{ marginTop: '1rem' }}>{error}</div>}
      {success && <div className="success" style={{ marginTop: '1rem' }}>{success}</div>}
    </div>
  )
}

export default StoreView
