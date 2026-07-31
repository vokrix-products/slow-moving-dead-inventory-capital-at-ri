import unittest
from unittest.mock import patch, MagicMock
import os

from processor import process_file

class TestProcessor(unittest.TestCase):
    @patch.dict(os.environ, {"DEEPSEEK_API_KEY": "fake-key"})
    @patch("processor.OpenAI")
    def test_process_file(self, mock_openai):
        # Configure the mock client
        mock_client_instance = MagicMock()
        mock_openai.return_value = mock_client_instance

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '''
[
  {
    "title": "Dead Product X",
    "status": "dead:critical",
    "details": {"capital_value": 30000, "sales_velocity": 0},
    "due_date": "2024-12-31"
  },
  {
    "title": "Slow Mover Y",
    "status": "slow_moving:warning",
    "details": {"capital_value": 5000, "sales_velocity": 3},
    "due_date": null
  }
]
        '''
        mock_client_instance.chat.completions.create.return_value = mock_response

        data = b"any text"
        result = process_file(data)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["title"], "Dead Product X")
        self.assertEqual(result[0]["status"], "dead:critical")
        self.assertEqual(result[0]["due_date"], "2024-12-31")
        self.assertIsNone(result[1]["due_date"])

if __name__ == "__main__":
    unittest.main()
