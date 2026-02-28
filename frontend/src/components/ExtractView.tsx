import { useState } from 'react'

interface FileMetadata {
  name: string
  contents: string[]
  creation_date: string
  extra: string
}

interface UploadedFile {
  name: string
  path: string
  size: number
  status: string
}

interface ExtractViewProps {
  onDataExtracted?: (data: FileMetadata[]) => void
}

function ExtractView({ onDataExtracted }: ExtractViewProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState<FileMetadata[] | null>(null)
  const [error, setError] = useState('')
  
  // File upload state
  const [selectedFiles, setSelectedFiles] = useState<FileList | null>(null)
  const [uploadStatus, setUploadStatus] = useState<{ uploaded: UploadedFile[], errors: any[] } | null>(null)
  const [isUploading, setIsUploading] = useState(false)

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setSelectedFiles(e.target.files)
      setUploadStatus(null)
    }
  }

  const handleUpload = async () => {
    if (!selectedFiles || selectedFiles.length === 0) {
      setError('Please select files to upload')
      return
    }

    setIsUploading(true)
    setError('')

    try {
      const formData = new FormData()
      
      // Append all files to the form data
      for (let i = 0; i < selectedFiles.length; i++) {
        formData.append('files', selectedFiles[i])
      }

      const response = await fetch('http://localhost:5004/files', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`)
      }

      const data = await response.json()
      setUploadStatus(data)
      
      // Show success message
      if (data.uploaded && data.uploaded.length > 0) {
        alert(`Successfully uploaded ${data.uploaded.length} file(s)!`)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload files')
    } finally {
      setIsUploading(false)
    }
  }

  const handleExtract = async () => {
    setIsLoading(true)
    setError('')
    setResult(null)

    try {
      // Call the backend /extract endpoint which uses the Python logic
      const response = await fetch('http://localhost:5004/extract', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        throw new Error(`Extract failed: ${response.statusText}`)
      }

      const data = await response.json()
      
      if (data.status === 'success') {
        setResult(data.data)
        // Pass the extracted data to parent component
        if (onDataExtracted) {
          onDataExtracted(data.data)
        }
      } else {
        throw new Error(data.detail || 'Unknown error')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to extract metadata')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div>
      <h2 style={{ marginBottom: '1.5rem' }}>Extract Metadata from Dataset</h2>
      
      {/* File Upload Section */}
      <div style={{ marginBottom: '2rem', padding: '1rem', border: '1px solid #ddd', borderRadius: '8px' }}>
        <h3 style={{ marginBottom: '1rem' }}>Upload Files</h3>
        <div className="form-group">
          <label htmlFor="fileInput">Select Files</label>
          <input
            id="fileInput"
            type="file"
            multiple
            onChange={handleFileSelect}
          />
        </div>
        
        <button 
          className="btn btn-secondary" 
          onClick={handleUpload}
          disabled={isUploading || !selectedFiles}
          style={{ marginTop: '1rem' }}
        >
          {isUploading ? 'Uploading...' : 'Upload Files'}
        </button>

        {uploadStatus && (
          <div style={{ marginTop: '0.5rem', color: 'green' }}>
            ✓ Uploaded: {uploadStatus.uploaded.length} file(s)
            {uploadStatus.errors && uploadStatus.errors.length > 0 && (
              <span style={{ color: 'red' }}> ✗ Errors: {uploadStatus.errors.length}</span>
            )}
          </div>
        )}
      </div>

      {/* Extract Button */}
      <button 
        className="btn btn-primary" 
        onClick={handleExtract}
        disabled={isLoading}
        style={{ marginBottom: '2rem' }}
      >
        {isLoading ? 'Extracting...' : 'Extract Metadata from Dataset'}
      </button>

      {error && <div className="error">{error}</div>}

      {result && (
        <div className="results">
          <h3 style={{ marginBottom: '1rem' }}>Extracted Documents ({result.length})</h3>
          
          <div className="stats">
            <div className="stat-card">
              <div className="stat-value">{result.length}</div>
              <div className="stat-label">Documents</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{result.filter(f => f.name.endsWith('.pdf')).length}</div>
              <div className="stat-label">PDFs</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{result.filter(f => f.name.endsWith('.txt')).length}</div>
              <div className="stat-label">Text Files</div>
            </div>
          </div>

          {result.map((file, index) => (
            <div key={index} className="result-item">
              <div className="result-header">
                <span className="result-title">{file.name}</span>
                <span className={`badge badge-${file.name.split('.').pop()}`}>
                  {file.name.split('.').pop()?.toUpperCase()}
                </span>
              </div>
              <div className="result-meta">
                <div>Created: {file.creation_date}</div>
                <div>Pages/Lines: {file.contents.length}</div>
              </div>
              {file.extra && file.extra !== '{}' && (
                <div className="result-extra">
                  <strong>Extra:</strong> {file.extra}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default ExtractView
