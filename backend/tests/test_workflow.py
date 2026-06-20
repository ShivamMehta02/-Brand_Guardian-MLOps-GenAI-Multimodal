import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Ensure we use the virtual environment's site-packages first to avoid global package mismatches
venv_site_packages = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.venv/Lib/site-packages"))
if os.path.exists(venv_site_packages):
    sys.path.insert(0, venv_site_packages)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.src.graph.workflow import app
from backend.src.graph.state import VideoAuditState

class TestBrandGuardianWorkflow(unittest.TestCase):
    
    @patch('backend.src.graph.nodes.VideoIndexerService')
    @patch('backend.src.graph.nodes.AzureChatOpenAI')
    @patch('backend.src.graph.nodes.AzureOpenAIEmbeddings')
    @patch('backend.src.graph.nodes.AzureSearch')
    def test_workflow_execution_success(self, mock_search, mock_embeddings, mock_llm, mock_vi_service):
        # 1. Setup mocks
        # Video Indexer Mock
        mock_vi_instance = MagicMock()
        mock_vi_instance.download_youtube_video.return_value = "temp_audit_video.mp4"
        mock_vi_instance.upload_video.return_value = "mock_azure_id"
        mock_vi_instance.wait_for_processing.return_value = {"insights": "some_insights"}
        
        # We want extract_data to return a dict that updates the state
        mock_vi_instance.extract_data.return_value = {
            "transcript": "This video contains some compliance statements.",
            "ocr_text": ["Warning", "Disclaimer"]
        }
        mock_vi_service.return_value = mock_vi_instance
        
        # LLM Mock
        mock_llm_instance = MagicMock()
        # Mocking LLM invoke call returning compliance results
        mock_response = MagicMock()
        mock_response.content = '{"status": "PASS", "compliance_results": [], "final_report": "Video complies with guidelines."}'
        mock_llm_instance.invoke.return_value = mock_response
        mock_llm.return_value = mock_llm_instance
        
        # Search and Embeddings Mocks
        mock_search_instance = MagicMock()
        mock_search_instance.similarity_search.return_value = []
        mock_search.return_value = mock_search_instance
        
        # 2. Run the LangGraph workflow
        initial_inputs = {
            "video_url": "https://www.youtube.com/watch?v=dT7S75eYhcQ",
            "video_id": "vid_test",
            "compliance_results": [],
            "errors": []
        }
        
        # Invoke compiled graph
        final_state = app.invoke(initial_inputs)
        
        # 3. Verify workflow completed and transitioned state
        self.assertEqual(final_state.get("video_id"), "vid_test")
        self.assertIn("transcript", final_state)
        self.assertEqual(final_state.get("transcript"), "This video contains some compliance statements.")
        self.assertEqual(final_state.get("final_status"), "PASS")
        self.assertIn("final_report", final_state)
        self.assertEqual(len(final_state.get("compliance_results")), 0)
        self.assertEqual(len(final_state.get("errors")), 0)

if __name__ == '__main__':
    unittest.main()
