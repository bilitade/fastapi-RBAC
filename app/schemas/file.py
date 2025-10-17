"""File management schemas."""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class FileUploadResponse(BaseModel):
    """Response after file upload."""
    filename: str
    stored_name: str
    filepath: str
    size: int
    category: str
    user_id: int
    upload_date: str
    indexed: bool = False
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "filename": "document.txt",
                "stored_name": "20250117_120000_document.txt",
                "filepath": "data/uploads/1/general/20250117_120000_document.txt",
                "size": 1024,
                "category": "general",
                "user_id": 1,
                "upload_date": "2025-01-17T12:00:00",
                "indexed": True
            }
        }
    )


class FileInfo(BaseModel):
    """File information."""
    filename: str
    filepath: str
    relative_path: str
    size: int
    user_id: Optional[int] = None
    category: str = "general"
    modified: str
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "filename": "document.txt",
                "filepath": "data/uploads/1/general/document.txt",
                "relative_path": "1/general/document.txt",
                "size": 1024,
                "user_id": 1,
                "category": "general",
                "modified": "2025-01-17T12:00:00"
            }
        }
    )


class FileListResponse(BaseModel):
    """List of files."""
    files: List[FileInfo]
    count: int
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "files": [
                    {
                        "filename": "document.txt",
                        "filepath": "data/uploads/1/general/document.txt",
                        "relative_path": "1/general/document.txt",
                        "size": 1024,
                        "user_id": 1,
                        "category": "general",
                        "modified": "2025-01-17T12:00:00"
                    }
                ],
                "count": 1
            }
        }
    )


class FileDeleteResponse(BaseModel):
    """File deletion response."""
    success: bool
    message: str
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "File deleted successfully"
            }
        }
    )

