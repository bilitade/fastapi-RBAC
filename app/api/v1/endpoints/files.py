"""File management endpoints - simple and efficient."""
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.responses import FileResponse
from app.schemas.file import (
    FileUploadResponse,
    FileListResponse,
    FileDeleteResponse
)
from app.ai.storage import FileStorage
from app.ai.documents import DocumentSearch
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    category: str = Query(default="general", description="File category"),
    index: bool = Query(default=True, description="Index file for AI search"),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Upload file to storage.
    
    - Saves to filesystem
    - Optionally indexes in vector DB for AI search
    - Supports .txt and .md files
    """
    # Validate file type
    allowed_types = [".txt", ".md"]
    file_ext = "." + file.filename.split(".")[-1].lower() if "." in file.filename else ""
    
    if file_ext not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not supported. Allowed: {', '.join(allowed_types)}"
        )
    
    # Save file
    storage = FileStorage()
    file_metadata = await storage.save_file(
        file=file,
        user_id=current_user.id,
        category=category
    )
    
    # Index if requested
    indexed = False
    if index:
        docs = DocumentSearch()
        indexed = docs.index_file(
            filepath=file_metadata["filepath"],
            metadata={
                "user_id": current_user.id,
                "user_email": current_user.email,
                "category": category,
                "upload_date": file_metadata["upload_date"]
            }
        )
    
    return {
        **file_metadata,
        "indexed": indexed
    }


@router.get("/list", response_model=FileListResponse)
async def list_files(
    category: Optional[str] = Query(None, description="Filter by category"),
    current_user: User = Depends(get_current_user)
) -> Any:
    """List user's uploaded files."""
    storage = FileStorage()
    files = storage.list_files(
        user_id=current_user.id,
        category=category
    )
    
    return {
        "files": files,
        "count": len(files)
    }


@router.get("/download/{relative_path:path}")
async def download_file(
    relative_path: str,
    current_user: User = Depends(get_current_user)
) -> FileResponse:
    """Download a file."""
    # Check if file belongs to user
    if not relative_path.startswith(f"{current_user.id}/"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    storage = FileStorage()
    filepath = storage.get_file_path(relative_path)
    
    if not filepath:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    return FileResponse(
        path=filepath,
        filename=filepath.name,
        media_type="application/octet-stream"
    )


@router.delete("/{relative_path:path}", response_model=FileDeleteResponse)
async def delete_file(
    relative_path: str,
    current_user: User = Depends(get_current_user)
) -> Any:
    """Delete a file."""
    # Check if file belongs to user
    if not relative_path.startswith(f"{current_user.id}/"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    storage = FileStorage()
    filepath = storage.get_file_path(relative_path)
    
    if not filepath:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    success = storage.delete_file(str(filepath))
    
    if success:
        return {
            "success": True,
            "message": "File deleted successfully"
        }
    else:
        return {
            "success": False,
            "message": "Failed to delete file"
        }


# Admin endpoints
@router.get("/admin/list", response_model=FileListResponse)
async def admin_list_files(
    user_id: Optional[int] = Query(None, description="Filter by user"),
    category: Optional[str] = Query(None, description="Filter by category"),
    current_user: User = Depends(get_current_user)
) -> Any:
    """List all files (admin only)."""
    from app.middleware.rbac import require_permissions
    
    # Check admin permission
    require_permissions(["user:read"])(current_user)
    
    storage = FileStorage()
    files = storage.list_files(
        user_id=user_id,
        category=category
    )
    
    return {
        "files": files,
        "count": len(files)
    }

