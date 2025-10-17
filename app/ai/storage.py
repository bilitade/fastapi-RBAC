"""Simple file storage service."""
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import UploadFile
from app.config import settings


class FileStorage:
    """Handle file uploads and storage."""
    
    def __init__(self):
        """Initialize file storage."""
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.max_size = settings.MAX_UPLOAD_SIZE
    
    async def save_file(
        self,
        file: UploadFile,
        user_id: int,
        category: str = "general"
    ) -> Dict[str, Any]:
        """
        Save uploaded file to filesystem.
        
        Args:
            file: Uploaded file
            user_id: ID of user uploading
            category: File category
            
        Returns:
            File metadata
        """
        # Read content first to check size
        content = await file.read()
        
        if len(content) > self.max_size:
            raise ValueError(f"File too large. Max size: {self.max_size / 1024 / 1024}MB")
        
        # Create user directory
        user_dir = self.upload_dir / str(user_id) / category
        user_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        filepath = user_dir / filename
        
        # Save file
        with open(filepath, "wb") as f:
            f.write(content)
        
        # Get file info
        file_stat = filepath.stat()
        
        return {
            "filename": file.filename,
            "stored_name": filename,
            "filepath": str(filepath),
            "relative_path": str(filepath.relative_to(self.upload_dir)),
            "size": file_stat.st_size,
            "category": category,
            "user_id": user_id,
            "upload_date": datetime.now().isoformat(),
            "content_type": file.content_type or "application/octet-stream"
        }
    
    def list_files(
        self,
        user_id: Optional[int] = None,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List files with optional filters."""
        files = []
        
        search_path = self.upload_dir
        if user_id:
            search_path = search_path / str(user_id)
            if category:
                search_path = search_path / category
        
        if not search_path.exists():
            return files
        
        for filepath in search_path.rglob("*"):
            if filepath.is_file():
                stat = filepath.stat()
                rel_path = filepath.relative_to(self.upload_dir)
                parts = rel_path.parts
                
                files.append({
                    "filename": filepath.name,
                    "filepath": str(filepath),
                    "relative_path": str(rel_path),
                    "size": stat.st_size,
                    "user_id": int(parts[0]) if parts else None,
                    "category": parts[1] if len(parts) > 1 else "general",
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        return files
    
    def delete_file(self, filepath: str) -> bool:
        """Delete a file."""
        try:
            path = Path(filepath)
            if path.exists() and path.is_file():
                path.unlink()
                return True
        except Exception:
            pass
        return False
    
    def get_file_path(self, relative_path: str) -> Optional[Path]:
        """Get full path from relative path."""
        path = self.upload_dir / relative_path
        return path if path.exists() else None

