# test_email_system.py
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import threading
import time
import smtplib
from http.server import HTTPServer

# Import the class to test
from email_system import EmailSender
from Db_maneger.Db_maneger import DBManager


class TestEmailSender(unittest.TestCase):
    """
    Test suite for EmailSender class - Unit Tests
    """

    def setUp(self):
        """Set up test fixtures before each test method"""
        # Arrange
        self.mock_db = Mock(spec=DBManager)
        self.email_sender = EmailSender(self.mock_db)
        self.email_sender.gmail_config = {
            'email': 'test@example.com',
            'app_password': 'test_password',
            'smtp_server': 'smtp.test.com',
            'smtp_port': 587
        }
        self.test_plate = "TEST-123-CD"

    def tearDown(self):
        """Clean up after each test method"""
        if hasattr(self.email_sender, 'server') and self.email_sender.server:
            try:
                self.email_sender.server.shutdown()
            except:
                pass

    # ============ INITIALIZATION TESTS ============
    def test_initialization_default_values(self):
        """Test that EmailSender initializes with correct default values"""
        self.assertIsNone(self.email_sender.decision)
        self.assertIsNone(self.email_sender.current_plate)
        self.assertIsNone(self.email_sender.server)
        self.assertFalse(self.email_sender._should_exit)
        self.assertEqual(self.email_sender.db, self.mock_db)

    # ============ send_vehicle_alert METHOD TESTS ============
    @patch('smtplib.SMTP')
    def test_send_vehicle_alert_success(self, mock_smtp):
        """Test successful email sending"""
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        result = self.email_sender.send_vehicle_alert(self.test_plate)
        
        self.assertTrue(result)
        self.assertEqual(self.email_sender.current_plate, self.test_plate)

    @patch('smtplib.SMTP')
    def test_send_vehicle_alert_smtp_failure(self, mock_smtp):
        """Test email sending failure when SMTP connection fails"""
        mock_smtp.side_effect = smtplib.SMTPException("SMTP connection failed")
        
        result = self.email_sender.send_vehicle_alert(self.test_plate)
        
        self.assertFalse(result)

    # ============ wait_for_decision METHOD TESTS ============
    def test_wait_for_decision_timeout(self):
        """Test wait_for_decision returning timeout"""
        result = self.email_sender.wait_for_decision(timeout=0.1)
        self.assertEqual(result, "timeout")

    def test_wait_for_decision_with_immediate_decision(self):
        """Test wait_for_decision when decision is already set"""
        self.email_sender.decision = 'accept_whitelist'
        result = self.email_sender.wait_for_decision(timeout=0.1)
        self.assertEqual(result, 'accept_whitelist')

    # ============ email_shutdown_system METHOD TESTS ============
    @patch.object(time, 'sleep')
    def test_email_shutdown_system_accept_whitelist(self, mock_sleep):
        """Test email_shutdown_system with ACCEPT + WHITELIST decision"""
        self.email_sender.decision = 'accept_whitelist'
        self.email_sender.current_plate = self.test_plate
        self.email_sender.server = MagicMock()
        
        self.email_sender.email_shutdown_system()
        
        self.mock_db.whitelist_plate.assert_called_once_with(self.test_plate)
        self.mock_db.add_license_plate.assert_called_once_with(self.test_plate, confidence=100)
        self.mock_db.save_data.assert_called_once()
        self.email_sender.server.shutdown.assert_called_once()
        self.assertTrue(self.email_sender._should_exit)

    @patch.object(time, 'sleep')
    def test_email_shutdown_system_accept_only(self, mock_sleep):
        """Test email_shutdown_system with ACCEPT ONLY decision"""
        self.email_sender.decision = 'accept_only'
        self.email_sender.current_plate = self.test_plate
        self.email_sender.server = MagicMock()
        
        self.email_sender.email_shutdown_system()
        
        self.mock_db.add_license_plate.assert_called_once_with(self.test_plate, confidence=100)
        self.mock_db.save_data.assert_called_once()
        self.email_sender.server.shutdown.assert_called_once()
        self.assertTrue(self.email_sender._should_exit)

    @patch.object(time, 'sleep')
    def test_email_shutdown_system_reject_blacklist(self, mock_sleep):
        """Test email_shutdown_system with REJECT + BLACKLIST decision"""
        self.email_sender.decision = 'reject_blacklist'
        self.email_sender.current_plate = self.test_plate
        self.email_sender.server = MagicMock()
        
        self.email_sender.email_shutdown_system()
        
        self.mock_db.blacklist_plate.assert_called_once_with(self.test_plate)
        self.mock_db.save_data.assert_called_once()
        self.email_sender.server.shutdown.assert_called_once()
        self.assertTrue(self.email_sender._should_exit)

    @patch.object(time, 'sleep')
    def test_email_shutdown_system_reject_only(self, mock_sleep):
        """Test email_shutdown_system with REJECT ONLY decision"""
        self.email_sender.decision = 'reject_only'
        self.email_sender.current_plate = self.test_plate
        self.email_sender.server = MagicMock()
        
        self.email_sender.email_shutdown_system()
        
        # Should NOT save data for reject_only
        self.mock_db.save_data.assert_not_called()
        # Should still shutdown the server
        self.email_sender.server.shutdown.assert_called_once()
        self.assertTrue(self.email_sender._should_exit)

    @patch.object(time, 'sleep')
    def test_email_shutdown_system_unknown_decision(self, mock_sleep):
        """Test email_shutdown_system with unknown decision"""
        self.email_sender.decision = 'unknown_decision'
        self.email_sender.current_plate = self.test_plate
        self.email_sender.server = MagicMock()
        
        self.email_sender.email_shutdown_system()
        
        # Should NOT save data for unknown decision
        self.mock_db.save_data.assert_not_called()
        # But should still shutdown the server
        self.email_sender.server.shutdown.assert_called_once()
        self.assertTrue(self.email_sender._should_exit)

    @patch.object(time, 'sleep')
    def test_email_shutdown_system_no_server(self, mock_sleep):
        """Test email_shutdown_system when no server is running"""
        self.email_sender.decision = 'accept_only'
        self.email_sender.current_plate = self.test_plate
        self.email_sender.server = None
        
        self.email_sender.email_shutdown_system()
        
        self.mock_db.add_license_plate.assert_called_once_with(self.test_plate, confidence=100)
        self.mock_db.save_data.assert_called_once()
        # No server to shutdown, should not crash
        self.assertTrue(self.email_sender._should_exit)

    # ============ run_email_system METHOD TESTS ============
    @patch.object(EmailSender, 'start_local_server')
    @patch.object(EmailSender, 'send_vehicle_alert')
    @patch.object(EmailSender, 'wait_for_decision')
    def test_run_email_system_success(self, mock_wait, mock_send, mock_start):
        """Test complete run_email_system method with success"""
        mock_start.return_value = True
        mock_send.return_value = True
        mock_wait.return_value = 'accept_whitelist'
        
        result = self.email_sender.run_email_system(self.test_plate)
        
        self.assertEqual(result, 'accept_whitelist')
        mock_start.assert_called_once()
        mock_send.assert_called_once_with(self.test_plate)
        mock_wait.assert_called_once_with(timeout=120)

    @patch.object(EmailSender, 'start_local_server')
    def test_run_email_system_server_failure(self, mock_start):
        """Test run_email_system when server fails to start"""
        mock_start.return_value = False
        
        result = self.email_sender.run_email_system(self.test_plate)
        
        self.assertEqual(result, "error")

    @patch.object(EmailSender, 'start_local_server')
    @patch.object(EmailSender, 'send_vehicle_alert')
    def test_run_email_system_email_failure(self, mock_send, mock_start):
        """Test run_email_system when email fails to send"""
        mock_start.return_value = True
        mock_send.return_value = False
        
        result = self.email_sender.run_email_system(self.test_plate)
        
        self.assertEqual(result, "error")

    # ============ EDGE CASE TESTS ============
    @patch.object(threading.Thread, 'start')
    @patch('email_system.HTTPServer')
    def test_start_local_server_success(self, mock_http_server, mock_thread_start):
        """Test successful server startup"""
        mock_server_instance = MagicMock()
        mock_http_server.return_value = mock_server_instance
        
        result = self.email_sender.start_local_server()
        
        self.assertTrue(result)
        mock_http_server.assert_called_once()
        mock_thread_start.assert_called_once()

    def test_set_and_get_current_plate(self):
        """Test setting and getting current plate"""
        self.email_sender.current_plate = "NEW-PLATE"
        self.assertEqual(self.email_sender.current_plate, "NEW-PLATE")

    def test_set_and_get_decision(self):
        """Test setting and getting decision"""
        self.email_sender.decision = "test_decision"
        self.assertEqual(self.email_sender.decision, "test_decision")


def run_tests():
    """Run all tests and print summary report"""
    print("=" * 60)
    print("RUNNING EMAILSENDER UNIT TESTS")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestEmailSender))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY REPORT")
    print("=" * 60)
    print(f"Total Tests Run: {result.testsRun}")
    print(f"Successful: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✓ ALL TESTS PASSED!")
    else:
        print("\n✗ Some tests need attention")
    
    return result


if __name__ == '__main__':
    run_tests()