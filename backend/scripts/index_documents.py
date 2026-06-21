"""
Knowledge Base Indexer
======================
Reads PDFs from backend/data/, chunks them, and stores vectors in a local
ChromaDB database. This script runs ONCE (or whenever PDFs change).

No external API keys required — uses local HuggingFace embeddings.

Usage:
    uv run python -m backend.scripts.index_documents

Output:
    ./chroma_db/   ← local vector database directory
"""

import os
import glob
import logging
from dotenv import load_dotenv

load_dotenv(override=True)

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("indexer")


def index_docs():
    """
    Reads PDFs, chunks them, and populates a local ChromaDB vector store.
    Uses all-MiniLM-L6-v2 embeddings (runs locally, no API key needed).
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_folder = os.path.join(current_dir, "../data")
    chroma_db_path = os.getenv("CHROMA_DB_PATH", "./chroma_db")

    logger.info("=" * 60)
    logger.info("Brand Guardian — Knowledge Base Indexer")
    logger.info(f"Data folder:   {os.path.abspath(data_folder)}")
    logger.info(f"ChromaDB path: {os.path.abspath(chroma_db_path)}")
    logger.info("Embedding model: all-MiniLM-L6-v2 (local, no API key)")
    logger.info("=" * 60)

    # 1. Load local embedding model (downloads ~90MB on first run, then cached)
    embedding_model = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    try:
        logger.info(f"Loading embedding model: {embedding_model}...")
        embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            cache_folder=os.getenv("SENTENCE_TRANSFORMERS_HOME", "./models")
        )
        logger.info("✓ Embedding model ready (384-dim vectors)")
    except Exception as e:
        logger.error(f"Failed to load embedding model: {e}")
        return

    # 2. Initialize ChromaDB (creates the directory if it doesn't exist)
    try:
        logger.info(f"Initializing ChromaDB at: {chroma_db_path}")
        vector_store = Chroma(
            collection_name="brand-guardian",
            embedding_function=embeddings,
            persist_directory=chroma_db_path
        )
        logger.info("✓ ChromaDB initialized")
    except Exception as e:
        logger.error(f"Failed to initialize ChromaDB: {e}")
        return

    # 3. Find PDFs
    pdf_files = glob.glob(os.path.join(data_folder, "*.pdf"))
    if not pdf_files:
        logger.warning(f"No PDFs found in {data_folder}. Add PDF files and re-run.")
        return

    logger.info(f"Found {len(pdf_files)} PDFs: {[os.path.basename(f) for f in pdf_files]}")

    all_splits = []

    # 4. Load and chunk each PDF
    for pdf_path in pdf_files:
        try:
            logger.info(f"Loading: {os.path.basename(pdf_path)}...")
            loader = PyPDFLoader(pdf_path)
            raw_docs = loader.load()

            # 1000-char chunks with 200-char overlap
            # Keeps context from bleeding across section boundaries
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            splits = splitter.split_documents(raw_docs)

            for split in splits:
                split.metadata["source"] = os.path.basename(pdf_path)

            all_splits.extend(splits)
            logger.info(f"  → {len(splits)} chunks")

        except Exception as e:
            logger.error(f"Failed to process {pdf_path}: {e}")

    # 5. Upload to ChromaDB
    if all_splits:
        logger.info(f"Indexing {len(all_splits)} chunks into ChromaDB...")
        try:
            vector_store.add_documents(documents=all_splits)
            logger.info("=" * 60)
            logger.info("✅ Indexing complete! Knowledge base is ready.")
            logger.info(f"   Chunks indexed: {len(all_splits)}")
            logger.info(f"   ChromaDB path:  {os.path.abspath(chroma_db_path)}")
            logger.info("=" * 60)
        except Exception as e:
            logger.error(f"Failed to write to ChromaDB: {e}")
    else:
        logger.warning("No documents were processed.")


if __name__ == "__main__":
    index_docs()