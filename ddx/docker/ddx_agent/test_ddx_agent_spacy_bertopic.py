import unittest
from unittest.mock import patch, MagicMock
from agent_main import DDXAgent  # Import DDXAgent from agent_main

class TestDDXAgent(unittest.TestCase):
    
    @patch("agent_main.spacy.load")  # Mock the spacy.load function in agent_main
    def test_load_spacy_model(self, mock_spacy_load):
        # Mock the SpaCy model object returned by spacy.load
        mock_nlp = MagicMock()
        mock_spacy_load.return_value = mock_nlp

        agent = DDXAgent()
        nlp = agent.load_spacy_model()

        # Ensure spacy.load was called at least once with "en_core_web_trf"
        mock_spacy_load.assert_called_with("en_core_web_trf")
        # Additional check to confirm exact call count if needed
        self.assertEqual(mock_spacy_load.call_count, 1)
        # Ensure the returned model is the mocked instance
        self.assertEqual(nlp, mock_nlp)
        self.assertIsNotNone(nlp)

    @patch("agent_main.TopicModelProcessor")  # Mock the TopicModelProcessor in agent_main
    def test_load_bertopic_model(self, mock_topic_processor_class):
        # Mock the TopicModelProcessor instance that would be created
        mock_topic_processor = MagicMock()
        mock_topic_processor_class.return_value = mock_topic_processor

        agent = DDXAgent()
        topic_processor = agent.load_bertopic_model()

        # Ensure TopicModelProcessor was called at least once with the expected path
        mock_topic_processor_class.assert_called_with("/docker-entrypoint-ddx.d/ddx_agent/resources/Merged_model_09_26_2024")
        # Additional check to confirm exact call count if needed
        self.assertEqual(mock_topic_processor_class.call_count, 1)
        # Ensure the returned processor is the mocked instance
        self.assertEqual(topic_processor, mock_topic_processor)
        self.assertIsNotNone(topic_processor)

if __name__ == '__main__':
    unittest.main()
