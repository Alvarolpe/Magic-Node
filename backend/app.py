from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import glob
import csv
import io
from pathlib import Path
from typing import List
from datetime import datetime

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
UPLOAD_FOLDER = '../dataset'
DATASET_FOLDER = '../dataset'
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'csv', 'xlsx', 'doc', 'docx'}

# In-memory storage for stored metadata (simulating database)
stored_metadata: List[dict] = []

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATASET_FOLDER, exist_ok=True)

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_metadata_from_files():
    """Extract metadata from files in the dataset folder"""
    files_data = []
    
    if not os.path.exists(DATASET_FOLDER):
        return files_data
    
    for doc in glob.glob(f"{DATASET_FOLDER}/*"):
        filename = os.path.basename(doc)
        ext = Path(doc).suffix.lower()
        
        file_info = {
            "name": filename,
            "contents": [],
            "creation_date": datetime.fromtimestamp(os.path.getctime(doc)).isoformat(),
            "extra": "{}"
        }
        
        # Extract text content based on file type
        if ext == '.txt':
            try:
                with open(doc, 'r', encoding='utf-8', errors='ignore') as f:
                    file_info["contents"] = [line.strip() for line in f.readlines()]
            except:
                pass
        elif ext == '.csv':
            try:
                with open(doc, 'r', encoding='utf-8', errors='ignore') as f:
                    file_info["contents"] = [line.strip() for line in f.readlines()]
            except:
                pass
        elif ext == '.pdf':
            # For PDF files, just mark that it's a PDF
            file_info["contents"] = ["[PDF content - extraction not available]"]
        
        files_data.append(file_info)
    
    return files_data

@app.post("/files")
async def upload_files(files: List[UploadFile] = File(...)):
    """
    Upload multiple files to the backend
    Expects: multipart/form-data with files array
    Returns: JSON list of uploaded file info
    """
    if not files or len(files) == 0:
        raise HTTPException(status_code=400, detail="No files provided")
    
    uploaded_files = []
    errors = []
    
    for file in files:
        if file and allowed_file(file.filename):
            filename = file.filename
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            
            # Save file
            content = await file.read()
            with open(filepath, 'wb') as f:
                f.write(content)
            
            uploaded_files.append({
                "name": filename,
                "path": filepath,
                "size": os.path.getsize(filepath),
                "status": "uploaded"
            })
        else:
            errors.append({
                "name": file.filename,
                "status": "error",
                "message": "File type not allowed or invalid filename"
            })
    
    return {
        "uploaded": uploaded_files,
        "errors": errors,
        "total": len(files)
    }

@app.get("/files")
async def list_files():
    """
    List all uploaded files
    """
    files = []
    for filename in os.listdir(UPLOAD_FOLDER):
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.isfile(filepath):
            files.append({
                "name": filename,
                "size": os.path.getsize(filepath)
            })
    return files

@app.delete("/files/{filename}")
async def delete_file(filename: str):
    """
    Delete a specific file
    """
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return {"status": "deleted", "filename": filename}
    raise HTTPException(status_code=404, detail="File not found")

@app.get("/extract")
async def extract_metadata_endpoint():
    """
    Extract metadata from files in the dataset folder
    Returns: JSON with status and list of extracted file data
    """
    try:
        files_data = extract_metadata_from_files()
        
        return {
            "status": "success",
            "data": files_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/store")
async def store_metadata(data: List[dict]):
    """
    Store metadata to database (in-memory for now)
    Expects: JSON array of file metadata
    Returns: Success status
    """
    global stored_metadata
    
    try:
        for item in data:
            stored_metadata.append({
                "name": item.get("name", ""),
                "contents": item.get("contents", []),
                "creation_date": item.get("creation_date", ""),
                "extra": item.get("extra", "{}"),
                "stored_at": datetime.now().isoformat()
            })
        
        return {
            "status": "success",
            "message": f"Successfully stored {len(data)} documents metadata"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/query")
async def query_documents(
    start_date: str = "",
    end_date: str = "",
    users_mentioned: str = "",
    reunion_result: str = ""
):
    """
    Query stored documents based on filters
    Returns: List of matching documents
    """
    try:
        results = []
        
        for item in stored_metadata:
            # Apply filters
            if start_date and item.get("creation_date", "") < start_date:
                continue
            if end_date and item.get("creation_date", "") > end_date:
                continue
            
            results.append({
                "name": item.get("name", ""),
                "creation_date": item.get("creation_date", ""),
                "author": item.get("extra", "{}"),
                "type": os.path.splitext(item.get("name", ""))[1][1:] or "unknown"
            })
        
        return {
            "status": "success",
            "data": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5004)
