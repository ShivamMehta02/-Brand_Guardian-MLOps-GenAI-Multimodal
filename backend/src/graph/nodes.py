import json
import os
import logging
import re
from typing import Dict, Any

from langchain_groq import ChatGroq
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.messages import SystemMessage, HumanMessage

from backend.src.graph.state import VideoAuditState, ComplianceIssue
from backend.src.services.video_indexer import VideoIndexerService

logger = logging.getLogger("brand-guardian")
logging.basicConfig(level=logging.INFO)

# ---------------------------------------------------------------------------
# Shared embedding model — loaded once at module import to avoid repeated
# disk reads on every request. all-MiniLM-L6-v2 is 90MB, runs on CPU.
# ---------------------------------------------------------------------------
_EMBEDDING_MODEL = None

def _get_embeddings() -> HuggingFaceEmbeddings:
    global _EMBEDDING_MODEL
    if _EMBEDDING_MODEL is None:
        model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        logger.info(f"Loading embedding model: {model_name}")
        _EMBEDDING_MODEL = HuggingFaceEmbeddings(
            model_name=model_name,
            cache_folder=os.getenv("SENTENCE_TRANSFORMERS_HOME", "./models")
        )
    return _EMBEDDING_MODEL


# ---------------------------------------------------------------------------
# NODE 1: INDEXER
# Downloads the YouTube video, runs Whisper transcription + frame OCR locally.
# No Azure services used.
# ---------------------------------------------------------------------------
def index_video_node(state: VideoAuditState) -> Dict[str, Any]:
    """
    Local video processing node.
    Replaces Azure Video Indexer with faster-whisper + pytesseract.
    """
    video_url = state.get("video_url")
    video_id_input = state.get("video_id", "vid_demo")

    logger.info(f"--- [Node: Indexer] Processing: {video_url} ---")

    local_filename = "temp_audit_video.mp4"

    try:
        vi_service = VideoIndexerService()

        # 1. DOWNLOAD via yt-dlp
        if "youtube.com" in video_url or "youtu.be" in video_url:
            local_path = vi_service.download_youtube_video(video_url, output_path=local_filename)
        else:
            raise Exception("Only YouTube URLs are supported.")

        # 2. PROCESS LOCALLY (Whisper transcription + pytesseract OCR)
        transcript = vi_service.transcribe_audio(local_path)
        ocr_text = vi_service.extract_ocr_text(local_path)
        duration = vi_service.get_duration(local_path)

        # 3. CLEANUP temp file immediately to free disk space
        if os.path.exists(local_path):
            os.remove(local_path)
            logger.info("Temp video file cleaned up.")

        logger.info("--- [Node: Indexer] Local processing complete ---")
        return {
            "transcript": transcript,
            "ocr_text": ocr_text,
            "video_metadata": {
                "duration": duration,
                "platform": "youtube"
            }
        }

    except Exception as e:
        logger.error(f"Video Processing Failed: {e}")
        return {
            "errors": [str(e)],
            "final_status": "FAIL",
            "transcript": "",
            "ocr_text": []
        }


# ---------------------------------------------------------------------------
# NODE 2: COMPLIANCE AUDITOR
# RAG retrieval from local ChromaDB + Gemini compliance reasoning.
# ---------------------------------------------------------------------------
def audit_content_node(state: VideoAuditState) -> Dict[str, Any]:
    """
    RAG-based compliance audit using local ChromaDB + Google Gemini.
    """
    logger.info("--- [Node: Auditor] Querying knowledge base & Gemini ---")

    transcript = state.get("transcript", "")

    if not transcript:
        logger.warning("No transcript available. Skipping audit.")
        return {
            "final_status": "FAIL",
            "final_report": "Audit skipped: video processing failed (no transcript)."
        }

    # --- Groq LLM (free, no CC, 100+ tok/s) ---
    # Default: llama-3.1-8b-instant — free, fast, excellent JSON output
    # Override with GROQ_MODEL=llama-3.3-70b-versatile for best reasoning
    llm = ChatGroq(
        model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
        temperature=0.0,
        api_key=os.getenv("GROQ_API_KEY"),
        max_tokens=1024
    )

    # --- ChromaDB vector store (local file, no cloud) ---
    chroma_db_path = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    vector_store = Chroma(
        collection_name="brand-guardian",
        embedding_function=_get_embeddings(),
        persist_directory=chroma_db_path
    )

    # --- RAG Retrieval ---
    ocr_text = state.get("ocr_text", [])
    # Truncate to 500 chars — enough for topic signal, avoids wasting embedding tokens
    query_text = transcript[:500]

    docs = vector_store.similarity_search(query_text, k=3)
    retrieved_rules = "\n\n".join([doc.page_content for doc in docs])

    if not retrieved_rules:
        logger.warning("No rules retrieved from ChromaDB. Run index_documents.py first.")

    # --- Build compliance audit prompt ---
    system_prompt = f"""You are a Brand Compliance Auditor.

OFFICIAL REGULATORY RULES:
{retrieved_rules}

Analyze the transcript and on-screen text. Identify any violations of the rules above.
Respond with ONLY valid JSON — no markdown, no explanation:

{{
    "compliance_results": [
        {{"category": "<rule category>", "severity": "CRITICAL|WARNING", "description": "<specific violation>"}}
    ],
    "status": "FAIL",
    "final_report": "<one-paragraph summary>"
}}

If no violations: set status to "PASS" and compliance_results to []."""

    user_message = f"""TRANSCRIPT: {transcript}
ON-SCREEN TEXT (OCR): {' | '.join(ocr_text) if ocr_text else 'None'}"""

    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ])

        # Strip markdown code fences if model wraps in ```json ... ```
        content = response.content
        if "```" in content:
            match = re.search(r"```(?:json)?(.*?)```", content, re.DOTALL)
            if match:
                content = match.group(1)

        audit_data = json.loads(content.strip())

        return {
            "compliance_results": audit_data.get("compliance_results", []),
            "final_status": audit_data.get("status", "FAIL"),
            "final_report": audit_data.get("final_report", "No report generated.")
        }

    except Exception as e:
        logger.error(f"Auditor node error: {str(e)}")
        logger.error(f"Raw LLM response: {response.content if 'response' in locals() else 'None'}")
        return {
            "errors": [str(e)],
            "final_status": "FAIL"
        }