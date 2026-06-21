import unittest
from unittest.mock import patch, MagicMock
import os
import sys

venv_site_packages = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.venv/Lib/site-packages"))
if os.path.exists(venv_site_packages):
    sys.path.insert(0, venv_site_packages)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.src.graph.workflow import app
from backend.src.graph.state import VideoAuditState


class TestBrandGuardianWorkflow(unittest.TestCase):

    @patch('backend.src.graph.nodes.VideoIndexerService')
    @patch('backend.src.graph.nodes.HuggingFaceEndpoint')   # ← was ChatGoogleGenerativeAI
    @patch('backend.src.graph.nodes.Chroma')
    @patch('backend.src.graph.nodes._get_embeddings')
    def test_workflow_execution_success(self, mock_get_embeddings, mock_chroma, mock_llm, mock_vi_service):
        """
        Tests the full LangGraph workflow with all external services mocked.
        Verifies: download → local processing → RAG → Gemini → final state.
        """
        # --- VideoIndexerService mock ---
        mock_vi_instance = MagicMock()
        mock_vi_instance.download_youtube_video.return_value = "temp_audit_video.mp4"
        mock_vi_instance.transcribe_audio.return_value = "This video contains compliance statements."
        mock_vi_instance.extract_ocr_text.return_value = ["Warning", "Disclaimer"]
        mock_vi_instance.get_duration.return_value = 120.0
        mock_vi_service.return_value = mock_vi_instance

        # HuggingFace LLM Mock (returns plain string, not .content object)
        mock_llm_instance = MagicMock()
        mock_llm_instance.invoke.return_value = '{"status": "PASS", "compliance_results": [], "final_report": "Video complies."}'
        mock_llm.return_value = mock_llm_instance

        # --- ChromaDB + embeddings mock ---
        mock_embeddings_instance = MagicMock()
        mock_get_embeddings.return_value = mock_embeddings_instance

        mock_chroma_instance = MagicMock()
        mock_chroma_instance.similarity_search.return_value = []
        mock_chroma.return_value = mock_chroma_instance

        # --- Run the workflow ---
        initial_inputs = {
            "tenant_id": "test_tenant",
            "video_url": "https://www.youtube.com/watch?v=dT7S75eYhcQ",
            "video_id": "vid_test",
            "compliance_results": [],
            "errors": []
        }

        final_state = app.invoke(initial_inputs)

        # --- Assertions ---
        self.assertEqual(final_state.get("video_id"), "vid_test")
        self.assertIn("transcript", final_state)
        self.assertEqual(final_state.get("transcript"), "This video contains compliance statements.")
        self.assertEqual(final_state.get("final_status"), "PASS")
        self.assertIn("final_report", final_state)
        self.assertEqual(len(final_state.get("compliance_results")), 0)
        self.assertEqual(len(final_state.get("errors")), 0)

        # Verify local processing methods were called (not Azure)
        mock_vi_instance.transcribe_audio.assert_called_once()
        mock_vi_instance.extract_ocr_text.assert_called_once()
        mock_vi_instance.get_duration.assert_called_once()


if __name__ == '__main__':
    unittest.main()
