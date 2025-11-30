"""
Integration tests for AI ontology components
"""

import unittest
from datetime import datetime
from nemesis.ai_ontology import ABCIntegrationLayer


class TestABCIntegration(unittest.TestCase):
    """Test ABC integration layer"""
    
    def setUp(self):
        self.abc = ABCIntegrationLayer()
    
    def test_process_intelligence_feed(self):
        """Test intelligence feed processing"""
        intelligence = [
            {"text": "Lazarus Group detected moving funds", "source": "twitter"}
        ]
        result = self.abc.process_intelligence_feed(intelligence)
        
        self.assertIn("entities", result)
        self.assertIn("relationships", result)
        self.assertIn("behavioral_signatures", result)
        self.assertIn("threat_forecasts", result)
    
    def test_natural_language_query(self):
        """Test natural language query"""
        response = self.abc.query_natural_language("Who is coordinating with Lazarus?")
        
        self.assertIn("query", response)
        self.assertIn("response", response)
        self.assertIn("structured_data", response)
    
    def test_record_feedback(self):
        """Test feedback recording"""
        feedback = self.abc.record_feedback(
            feedback_type="true_positive",
            entity_id="test_actor",
            actual_outcome={"detected": True}
        )
        
        self.assertEqual(feedback.entity_id, "test_actor")
        self.assertIsNotNone(feedback.feedback_id)


if __name__ == '__main__':
    unittest.main()

