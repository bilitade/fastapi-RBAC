"""Simple document search with vector store."""
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.config import settings


class DocumentSearch:
    """Simple document search with metadata."""
    
    def __init__(self):
        """Initialize document search."""
        self.vector_path = settings.VECTOR_STORE_PATH
        self.embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
    
    def load_documents(self, directory: str) -> List[Document]:
        """Load documents from directory."""
        docs = []
        path = Path(directory)
        
        if not path.exists():
            return docs
        
        # Load text and markdown files
        for pattern in ["**/*.txt", "**/*.md"]:
            for file in path.glob(pattern):
                try:
                    loader = TextLoader(str(file))
                    loaded_docs = loader.load()
                    
                    # Add metadata
                    for doc in loaded_docs:
                        stat = file.stat()
                        doc.metadata.update({
                            "filename": file.name,
                            "filepath": str(file),
                            "size": stat.st_size,
                            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            "type": file.suffix[1:] if file.suffix else "txt"
                        })
                    
                    docs.extend(loaded_docs)
                except Exception:
                    continue
        
        return docs
    
    def index_file(
        self,
        filepath: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Index a single file with metadata.
        
        Args:
            filepath: Path to file
            metadata: Additional metadata (user_id, category, etc.)
            
        Returns:
            Success status
        """
        try:
            path = Path(filepath)
            if not path.exists():
                return False
            
            # Load document
            loader = TextLoader(str(path))
            docs = loader.load()
            
            # Add metadata
            for doc in docs:
                stat = path.stat()
                doc.metadata.update({
                    "filename": path.name,
                    "filepath": str(path),
                    "size": stat.st_size,
                    "indexed_at": datetime.now().isoformat(),
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "type": path.suffix[1:] if path.suffix else "txt"
                })
                
                # Add custom metadata
                if metadata:
                    doc.metadata.update(metadata)
            
            # Split and index
            texts = self.splitter.split_documents(docs)
            
            # Add to existing index or create new
            store = self.load_index()
            if store:
                store.add_documents(texts)
            else:
                os.makedirs(self.vector_path, exist_ok=True)
                Chroma.from_documents(
                    documents=texts,
                    embedding=self.embeddings,
                    persist_directory=self.vector_path
                )
            
            return True
        except Exception:
            return False
    
    def create_index(self, documents: List[Document]) -> Chroma:
        """Create vector store from documents."""
        texts = self.splitter.split_documents(documents)
        os.makedirs(self.vector_path, exist_ok=True)
        
        return Chroma.from_documents(
            documents=texts,
            embedding=self.embeddings,
            persist_directory=self.vector_path
        )
    
    def load_index(self) -> Optional[Chroma]:
        """Load existing vector store."""
        if not os.path.exists(self.vector_path):
            return None
        
        try:
            return Chroma(
                persist_directory=self.vector_path,
                embedding_function=self.embeddings
            )
        except Exception:
            return None
    
    async def search(self, query: str, k: int = 5) -> List[Document]:
        """Search documents."""
        store = self.load_index()
        if store is None:
            return []
        
        return await store.asimilarity_search(query, k=k)

