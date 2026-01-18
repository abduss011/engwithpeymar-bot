import os
import unittest
from unittest.mock import patch, MagicMock
os.environ["OPENAI_API_KEY"] = "dummy"

from bot.services import user_service, ai_service
import json

class TestUserService(unittest.TestCase):
    def setUp(self):
        self.test_file = 'test_users.json'
        self.patcher = patch('bot.services.user_service.USERS_FILE', self.test_file)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_set_and_get_user_level(self):
        user_service.set_user_level(123, "B2")
        self.assertEqual(user_service.get_user_level(123), "B2")
        self.assertIsNone(user_service.get_user_level(456))

    def test_persistence(self):
        user_service.set_user_level(123, "A1")
        with open(self.test_file, 'r') as f:
            data = json.load(f)
        self.assertEqual(data['123']['level'], "A1")

class TestAIService(unittest.TestCase):
    @patch('bot.services.ai_service.client')
    def test_generate_word_of_the_day(self, mock_client):
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Apple: A fruit."
        mock_client.chat.completions.create.return_value = mock_response

        result = ai_service.generate_word_of_the_day("A1")
        self.assertEqual(result, "Apple: A fruit.")
        mock_client.chat.completions.create.assert_called_once()

    @patch('bot.services.ai_service.client')
    def test_correct_sentence(self, mock_client):
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Corrected sentence."
        mock_client.chat.completions.create.return_value = mock_response

        result = ai_service.correct_sentence("I goes", "B1")
        self.assertEqual(result, "Corrected sentence.")

if __name__ == '__main__':
    unittest.main()
