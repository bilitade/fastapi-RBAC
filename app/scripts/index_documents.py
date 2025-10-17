"""
Script to index documents into vector store for AI search.

Usage:
    python -m app.scripts.index_documents /path/to/documents
"""
import sys
from pathlib import Path
from app.ai.documents import DocumentSearch


def index_documents(directory_path: str) -> None:
    """Index documents from directory into vector store."""
    print(f"📁 Loading documents from: {directory_path}")
    
    docs = DocumentSearch()
    
    # Load documents
    documents = docs.load_documents(directory_path)
    print(f"✓ Loaded {len(documents)} documents")
    
    if not documents:
        print("⚠ No documents found to index")
        return
    
    # Create vector store
    print("🔄 Creating vector store...")
    vector_store = docs.create_index(documents)
    print(f"✓ Vector store created at: {docs.vector_path}")
    print(f"✓ Indexed {len(documents)} documents")
    
    print("\n✅ Document indexing complete!")
    print(f"📊 Documents are now searchable via AI endpoints")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m app.scripts.index_documents /path/to/documents")
        print("\nExample:")
        print("  python -m app.scripts.index_documents ./docs")
        sys.exit(1)
    
    directory = sys.argv[1]
    
    if not Path(directory).exists():
        print(f"✗ Error: Directory not found: {directory}")
        sys.exit(1)
    
    index_documents(directory)

