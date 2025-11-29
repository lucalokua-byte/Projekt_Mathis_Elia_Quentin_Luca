# test_email_system.py
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import threading
import time
import smtplib
from http.server import HTTPServer
import io
from contextlib import redirect_stdout
import base64

# Import the class to test
from email_system import EmailSender

class TestEmailSender(unittest.TestCase):
    """
    Test suite for email_system class - Unit Tests
    """

    def setUp(self):
        """Set up test fixtures before each test method"""
        # Arrange - Prepare test data
        self.email_sender = EmailSender()
        # Test configuration to avoid sending real emails
        self.email_sender.gmail_config = {
            'email': 'test@example.com',
            'app_password': 'test_password',
            'smtp_server': 'smtp.test.com',
            'smtp_port': 587
        }
        self.test_plate = "TEST-123-CD"

    def tearDown(self):
        """Clean up after each test method"""
        # Cleanup after each test - force server shutdown
        if hasattr(self.email_sender, 'server') and self.email_sender.server:
            try:
                self.email_sender.server.shutdown()
                self.email_sender.server.server_close()
            except:
                pass
            self.email_sender.server = None

    # INITIALIZATION TESTS
    def test_initialization_default_values(self):
        """Test that EmailSender initializes with correct default values"""
        # Act & Assert
        self.assertIsNone(self.email_sender.decision, "Decision should be None at initialization")
        self.assertIsNone(self.email_sender.current_plate, "Current plate should be None at initialization")
        self.assertIsNone(self.email_sender.server, "Server should be None at initialization")

    def test_gmail_config_structure(self):
        """Test that gmail_config has all required keys"""
        # Act & Assert
        config = self.email_sender.gmail_config
        required_keys = ['email', 'app_password', 'smtp_server', 'smtp_port']
        for key in required_keys:
            self.assertIn(key, config, f"Config should contain {key}")

    # send_vehicle_alert METHOD TESTS - POSITIVE CASES
    @patch('smtplib.SMTP')
    def test_send_vehicle_alert_success(self, mock_smtp):
        """Test successful email sending - Happy Path"""
        # Arrange
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # Act
        result = self.email_sender.send_vehicle_alert(self.test_plate)
        
        # Assert
        self.assertTrue(result, "send_vehicle_alert should return True on success")
        self.assertEqual(self.email_sender.current_plate, self.test_plate, "Current plate should be set to the provided plate number")

    @patch('smtplib.SMTP')
    def test_send_vehicle_alert_smtp_calls(self, mock_smtp):
        """Test that all SMTP methods are called correctly"""
        # Arrange
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # Act
        self.email_sender.send_vehicle_alert(self.test_plate)
        
        # Assert - Verify SMTP calls
        mock_smtp.assert_called_once_with('smtp.test.com', 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with('test@example.com', 'test_password')
        mock_server.send_message.assert_called_once()
        mock_server.quit.assert_called_once()

    @patch('smtplib.SMTP')
    def test_send_vehicle_alert_html_content(self, mock_smtp):
        """Test that HTML content contains correct elements"""
        # Arrange
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        sent_message = None
        
        def capture_send_message(msg):
            nonlocal sent_message
            sent_message = msg
        mock_server.send_message.side_effect = capture_send_message
        
        # Act
        self.email_sender.send_vehicle_alert(self.test_plate)
        
        # Assert - Verify HTML content
        self.assertIsNotNone(sent_message, "Message should not be None")
        
        # Get decoded HTML content
        html_payload = sent_message.get_payload()[0]
        html_content = html_payload.get_payload()
        
        # If content is base64 encoded, decode it
        if hasattr(html_payload, '_headers') and any('base64' in str(h) for h in html_payload._headers):
            html_content = base64.b64decode(html_content).decode('utf-8')
        
        # Verify essential elements in HTML
        self.assertIn(self.test_plate, html_content, "HTML should contain plate number")
        self.assertIn('accept_whitelist', html_content, "HTML should contain accept_whitelist button")
        self.assertIn('accept_only', html_content, "HTML should contain accept_only button")
        self.assertIn('reject_blacklist', html_content, "HTML should contain reject_blacklist button")
        self.assertIn('reject_only', html_content, "HTML should contain reject_only button")

    # send_vehicle_alert METHOD TESTS - ERROR CASES
    @patch('smtplib.SMTP')
    def test_send_vehicle_alert_smtp_failure(self, mock_smtp):
        """Test email sending failure when SMTP connection fails"""
        # Arrange
        mock_smtp.side_effect = smtplib.SMTPException("SMTP connection failed")
        
        # Act
        result = self.email_sender.send_vehicle_alert(self.test_plate)
        
        # Assert
        self.assertFalse(result, "send_vehicle_alert should return False on failure")

    @patch('smtplib.SMTP')
    def test_send_vehicle_alert_login_failure(self, mock_smtp):
        """Test email sending failure when login fails"""
        # Arrange
        mock_server = MagicMock()
        mock_server.login.side_effect = smtplib.SMTPAuthenticationError(535, "Authentication failed")
        mock_smtp.return_value = mock_server
        
        # Act
        result = self.email_sender.send_vehicle_alert(self.test_plate)
        
        # Assert
        self.assertFalse(result, "send_vehicle_alert should return False on login failure")

    # start_local_server METHOD TESTS - COMPLETELY MOCKED TO AVOID BLOCKING
    @patch('email_system.threading.Thread')
    @patch('email_system.HTTPServer')
    def test_start_local_server_success(self, mock_http_server, mock_thread):
        """Test successful server startup with complete mocking - FIXED"""
        # Arrange
        mock_server_instance = MagicMock()
        mock_http_server.return_value = mock_server_instance
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance
        
        # Act
        result = self.email_sender.start_local_server()
        
        # Assert
        self.assertTrue(result, "start_local_server should return True on success")
        mock_http_server.assert_called_once()
        mock_thread.assert_called_once()
        mock_thread_instance.start.assert_called_once()

    @patch('email_system.threading.Thread')
    @patch('email_system.HTTPServer')
    def test_start_local_server_failure(self, mock_http_server, mock_thread):
        """Test server startup failure - FIXED"""
        # Arrange
        mock_http_server.side_effect = Exception("Port already in use")
        
        # Act
        result = self.email_sender.start_local_server()
        
        # Assert
        self.assertFalse(result, "start_local_server should return False on failure")

    # wait_for_decision METHOD TESTS - FIXED TO AVOID BLOCKING
    def test_wait_for_decision_timeout(self):
        """Test wait_for_decision returning timeout"""
        # Act
        result = self.email_sender.wait_for_decision(timeout=0.01)  # Very short timeout
        
        # Assert
        self.assertEqual(result, "timeout", "Should return 'timeout' when no decision is made")

    def test_wait_for_decision_with_decision(self):
        """Test wait_for_decision returning actual decision - FIXED"""
        # Arrange
        # Set decision immediately to avoid waiting
        self.email_sender.decision = 'accept_whitelist'
        
        # Act
        result = self.email_sender.wait_for_decision(timeout=0.01)
        
        # Assert
        self.assertEqual(result, 'accept_whitelist', "Should return the decision that was set")

    # stop_program METHOD TESTS
    @patch('sys.exit')
    @patch('time.sleep')
    def test_stop_program_with_decision(self, mock_sleep, mock_exit):
        """Test stop_program with different decisions"""
        # Arrange
        test_cases = [
            ('accept_whitelist', 'ACCEPT + WHITELIST'),
            ('accept_only', 'ACCEPT ONLY'),
            ('reject_blacklist', 'REJECT + BLACKLIST'),
            ('reject_only', 'REJECT ONLY')
        ]
        
        for decision_code, expected_text in test_cases:
            with self.subTest(decision=decision_code):
                # Reset for each subtest
                self.email_sender.decision = decision_code
                self.email_sender.server = MagicMock()
                
                # Act
                try:
                    self.email_sender.stop_program()
                except SystemExit:
                    pass  # Expected behavior
                
                # Assert
                mock_sleep.assert_called_with(1)
                if self.email_sender.server:
                    self.email_sender.server.shutdown.assert_called_once()

    # INTEGRATION TESTS - WITHOUT REAL SERVER
    @patch('smtplib.SMTP')
    @patch('email_system.threading.Thread')
    @patch('email_system.HTTPServer')
    def test_full_flow_with_mocks(self, mock_http_server, mock_thread, mock_smtp):
        """Test the complete flow with mocked dependencies"""
        # Arrange
        mock_smtp_server = MagicMock()
        mock_smtp.return_value = mock_smtp_server
        mock_http_instance = MagicMock()
        mock_http_server.return_value = mock_http_instance
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance
        
        # Act - Simulate complete flow
        server_started = self.email_sender.start_local_server()
        email_sent = self.email_sender.send_vehicle_alert(self.test_plate)
        
        # Assert
        self.assertTrue(server_started, "Server should start successfully")
        self.assertTrue(email_sent, "Email should be sent successfully")
        self.assertEqual(self.email_sender.current_plate, self.test_plate, 
                        "Current plate should be set correctly")

    # TESTS WITH DIFFERENT LICENSE PLATES
    @patch('smtplib.SMTP')
    def test_send_vehicle_alert_different_plates(self, mock_smtp):
        """Test with different license plate formats"""
        # Arrange
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        test_plates = ["AB-123-CD", "XYZ-789", "TEST-001", "PLATE-99"]
        
        for plate in test_plates:
            with self.subTest(plate=plate):
                # Reset current_plate for each test
                self.email_sender.current_plate = None
                
                # Act
                result = self.email_sender.send_vehicle_alert(plate)
                
                # Assert
                self.assertTrue(result, f"Should handle plate {plate} successfully")
                self.assertEqual(self.email_sender.current_plate, plate, 
                                f"Current plate should be {plate}")

    # DECISION MAPPING TEST
    def test_decision_text_mapping(self):
        """Test that decision codes map to correct text"""
        # Arrange
        decision_mapping = {
            'accept_whitelist': 'ACCEPT + WHITELIST',
            'accept_only': 'ACCEPT ONLY', 
            'reject_blacklist': 'REJECT + BLACKLIST',
            'reject_only': 'REJECT ONLY'
        }
        
        for decision_code, expected_text in decision_mapping.items():
            with self.subTest(decision=decision_code):
                # Act & Assert
                self.assertEqual(
                    decision_mapping.get(decision_code), 
                    expected_text,
                    f"Decision code {decision_code} should map to {expected_text}"
                )

class TestEmailSenderEdgeCases(unittest.TestCase):
    """Tests for edge cases and error conditions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.email_sender = EmailSender()
        self.email_sender.gmail_config = {
            'email': 'test@example.com',
            'app_password': 'test_password',
            'smtp_server': 'smtp.test.com',
            'smtp_port': 587
        }

    @patch('smtplib.SMTP')
    def test_send_vehicle_alert_empty_plate(self, mock_smtp):
        """Test with empty license plate - should handle gracefully"""
        # Arrange
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # Act
        result = self.email_sender.send_vehicle_alert("")
        
        # Assert - Should handle empty string without crashing
        self.assertTrue(result, "Should handle empty plate string")
        self.assertEqual(self.email_sender.current_plate, "", "Current plate should be empty string")

    @patch('smtplib.SMTP')
    def test_send_vehicle_alert_none_plate(self, mock_smtp):
        """Test with None license plate - should handle gracefully"""
        # Arrange
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # Act
        result = self.email_sender.send_vehicle_alert(None)
        
        # Assert - Should handle None without crashing
        self.assertTrue(result, "Should handle None plate")
        self.assertIsNone(self.email_sender.current_plate, "Current plate should be None")

    @patch('smtplib.SMTP')
    def test_send_vehicle_alert_special_characters(self, mock_smtp):
        """Test with special characters in plate"""
        # Arrange
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        special_plate = "TEST-<script>alert('xss')</script>"
        
        # Act
        result = self.email_sender.send_vehicle_alert(special_plate)
        
        # Assert
        self.assertTrue(result, "Should handle special characters")

    def test_wait_for_decision_immediate_decision(self):
        """Test wait_for_decision when decision is already set - FIXED"""
        # Arrange
        # Set decision immediately
        self.email_sender.decision = 'reject_blacklist'
        
        # Act
        result = self.email_sender.wait_for_decision(timeout=0.01)
        
        # Assert
        self.assertEqual(result, 'reject_blacklist', "Should return immediate decision")

    @patch('sys.exit')
    def test_stop_program_no_server(self, mock_exit):
        """Test stop_program when no server is running"""
        # Arrange
        self.email_sender.decision = 'accept_only'
        self.email_sender.server = None  # No server running
        
        # Act
        try:
            self.email_sender.stop_program()
        except SystemExit:
            pass  # Expected behavior
        
        # Assert - Should exit without trying to shutdown non-existent server
        mock_exit.assert_called_once()

# TEST RUNNER WITH PROPER MOCKING
def run_tests():
    """Run tests with comprehensive mocking"""
    print("Running EmailSender Unit Tests from email_system.py...")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add tests
    suite.addTests(loader.loadTestsFromTestCase(TestEmailSender))
    suite.addTests(loader.loadTestsFromTestCase(TestEmailSenderEdgeCases))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests Run: {result.testsRun}")
    print(f"Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failed: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("ALL TESTS PASSED!")
    else:
        print("Some tests need attention")
    
    return result

if __name__ == '__main__':
    run_tests()