import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# PATH CONFIGURATION

# Get the absolute path to the project root directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add the project root to Python's module search path
sys.path.insert(0, project_root)

# Specifically add the Coding directory for module imports
coding_dir = os.path.join(project_root, 'Coding')
if os.path.exists(coding_dir):
    sys.path.insert(0, coding_dir)

# MOCK SETUP FOR EXTERNAL DEPENDENCIES

# Create mock for Interface module
sys.modules['Interface'] = MagicMock()
sys.modules['Interface.AbstractDBManager'] = MagicMock()

# Define a mock class to simulate the DBManager behavior
class MockDBManager:
    """Mock implementation of DBManager for testing purposes."""
    
    def __init__(self, *args, **kwargs):
        """Initialize mock DBManager."""
        pass
    
    def whitelist_plate(self, plate):
        """Mock method to whitelist a license plate."""
        return f"Mock: Whitelisting plate {plate}"
    
    def blacklist_plate(self, plate):
        """Mock method to blacklist a license plate."""
        return f"Mock: Blacklisting plate {plate}"
    
    def add_license_plate(self, plate, confidence):
        """Mock method to add a license plate with confidence score."""
        return f"Mock: Adding plate {plate} with confidence {confidence}"
    
    def save_data(self):
        """Mock method to save data."""
        return "Mock: Saving data"

# Replace the actual DBManager module with our mock
sys.modules['Db_maneger'] = MagicMock()
sys.modules['Db_maneger.Db_maneger'] = MagicMock()
sys.modules['Db_maneger.Db_maneger'].DBManager = MockDBManager

# IMPORT EMAILSENDER

try:
    # Import the EmailSender class from the actual module
    from Coding.mail_system.email_system import EmailSender
except ImportError as e:
    print(f"Import error: {e}")
    raise

# MAIN TEST CLASS FOR EMAILSENDER

class TestEmailSender(unittest.TestCase):
    """Unit tests for the EmailSender class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_db = MockDBManager()
        self.sender = EmailSender(self.mock_db)
    
    def test_initialization(self):
        """Test that EmailSender initializes with correct default values."""
        # Verify Gmail configuration
        self.assertEqual(self.sender.gmail_config['email'], 'projetseqlem@gmail.com')
        self.assertEqual(self.sender.gmail_config['smtp_server'], 'smtp.gmail.com')
        self.assertEqual(self.sender.gmail_config['smtp_port'], 587)
        
        # Verify state variables are initialized correctly
        self.assertIsNone(self.sender.decision)
        self.assertIsNone(self.sender.current_plate)
        self.assertIsNone(self.sender.server)
        self.assertFalse(self.sender._should_exit)
        self.assertEqual(self.sender.db, self.mock_db)
    
    @patch('smtplib.SMTP')
    def test_send_vehicle_alert_success(self, mock_smtp):
        """Test successful email sending with valid SMTP connection."""
        # Setup mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # Suppress print statements during test
        with patch('builtins.print'):
            result = self.sender.send_vehicle_alert("AB-123-CD")
        
        # Verify the result and state changes
        self.assertTrue(result)
        self.assertEqual(self.sender.current_plate, "AB-123-CD")
        
        # Verify SMTP calls were made correctly
        mock_smtp.assert_called_once_with('smtp.gmail.com', 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with('projetseqlem@gmail.com', 'nkab tgue nvqk xkrs')
        mock_server.send_message.assert_called_once()
        mock_server.quit.assert_called_once()
    
    @patch('smtplib.SMTP')
    def test_send_vehicle_alert_failure(self, mock_smtp):
        """Test email sending failure when SMTP connection fails."""
        # Simulate SMTP connection error
        mock_smtp.side_effect = Exception("SMTP Connection Error")
        
        with patch('builtins.print'):
            result = self.sender.send_vehicle_alert("XY-789-ZZ")
        
        self.assertFalse(result)
        self.assertEqual(self.sender.current_plate, "XY-789-ZZ")
    
    def test_cleanup_system_accept_whitelist(self):
        """Test cleanup system for 'accept_whitelist' decision."""
        self.sender.server = MagicMock()
        self.sender.decision = 'accept_whitelist'
        self.sender.current_plate = "TEST-001"
        
        with patch('builtins.print'):
            self.sender.cleanup_system()
        
        self.sender.server.shutdown.assert_called_once()
        self.assertTrue(self.sender._should_exit)
    
    def test_cleanup_system_accept_only(self):
        """Test cleanup system for 'accept_only' decision."""
        self.sender.server = MagicMock()
        self.sender.decision = 'accept_only'
        self.sender.current_plate = "TEST-003"
        
        with patch('builtins.print'):
            self.sender.cleanup_system()
        
        self.sender.server.shutdown.assert_called_once()
        self.assertTrue(self.sender._should_exit)
    
    def test_cleanup_system_reject_blacklist(self):
        """Test cleanup system for 'reject_blacklist' decision."""
        self.sender.server = MagicMock()
        self.sender.decision = 'reject_blacklist'
        self.sender.current_plate = "TEST-004"
        
        with patch('builtins.print'):
            self.sender.cleanup_system()
        
        self.sender.server.shutdown.assert_called_once()
        self.assertTrue(self.sender._should_exit)
    
    def test_cleanup_system_reject_only(self):
        """Test cleanup system for 'reject_only' decision (early return case)."""
        self.sender.server = MagicMock()
        self.sender.decision = 'reject_only'
        self.sender.current_plate = "TEST-002"
        
        with patch('builtins.print'):
            self.sender.cleanup_system()
        
        # For 'reject_only', the real code has an early return
        # Server should NOT be shut down in this case
        self.sender.server.shutdown.assert_not_called()
        self.assertFalse(self.sender._should_exit)
    
    def test_cleanup_system_unknown_decision(self):
        """Test cleanup system for unknown decision."""
        self.sender.server = MagicMock()
        self.sender.decision = 'unknown_decision'
        self.sender.current_plate = "TEST-005"
        
        with patch('builtins.print'):
            self.sender.cleanup_system()
        
        self.sender.server.shutdown.assert_called_once()
        self.assertTrue(self.sender._should_exit)
    
    def test_wait_for_decision_with_decision(self):
        """Test waiting for decision when decision is already made."""
        self.sender.decision = 'accept_only'
        
        with patch('builtins.print'):
            result = self.sender.wait_for_decision(timeout=1)
        
        self.assertEqual(result, 'accept_only')
    
    def test_wait_for_decision_timeout(self):
        """Test waiting for decision timeout when no decision is made."""
        with patch('builtins.print'):
            result = self.sender.wait_for_decision(timeout=0.1)
        
        self.assertEqual(result, "timeout")
    
    def test_wait_for_decision_should_exit(self):
        """Test waiting for decision when exit flag is set."""
        self.sender._should_exit = True
        
        with patch('builtins.print'):
            result = self.sender.wait_for_decision(timeout=5)
        
        # Should return "exit_no_decision" when exit flag is True and no decision
        self.assertEqual(result, "exit_no_decision")
    
    def test_wait_for_decision_should_exit_with_decision(self):
        """Test waiting for decision when exit flag is set but decision exists."""
        self.sender._should_exit = True
        self.sender.decision = 'accept_only'
        
        with patch('builtins.print'):
            result = self.sender.wait_for_decision(timeout=5)
        
        # Should return the decision when exit flag is True but decision exists
        self.assertEqual(result, 'accept_only')
    
    @patch('Coding.mail_system.email_system.HTTPServer')
    @patch('Coding.mail_system.email_system.threading.Thread')
    def test_start_local_server_success(self, mock_thread, mock_httpserver):
        """Test successful local server startup."""
        mock_server_instance = MagicMock()
        mock_httpserver.return_value = mock_server_instance
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance
        
        with patch('builtins.print'):
            result = self.sender.start_local_server()
        
        self.assertTrue(result)
        mock_httpserver.assert_called_once()
        mock_thread.assert_called_once()
        mock_thread_instance.start.assert_called_once()
        self.assertTrue(mock_thread_instance.daemon)
    
    @patch('Coding.mail_system.email_system.HTTPServer')
    def test_start_local_server_failure(self, mock_httpserver):
        """Test local server startup failure."""
        error_msg = "[Errno 10048] Port 8080 already in use"
        mock_httpserver.side_effect = OSError(error_msg)
        
        with patch('Coding.mail_system.email_system.threading.Thread'), \
             patch('builtins.print'):
            result = self.sender.start_local_server()
        
        self.assertFalse(result)
        self.assertIsNone(self.sender.server)
    
    @patch.object(EmailSender, 'start_local_server')
    @patch.object(EmailSender, 'send_vehicle_alert')
    @patch.object(EmailSender, 'wait_for_decision')
    def test_run_email_system_success(self, mock_wait, mock_send, mock_start):
        """Test complete email system execution with success."""
        mock_start.return_value = True
        mock_send.return_value = True
        mock_wait.return_value = 'accept_whitelist'
        
        with patch('builtins.print'):
            result = self.sender.run_email_system("PLATE-123")
        
        self.assertEqual(result, 'accept_whitelist')
        mock_start.assert_called_once()
        mock_send.assert_called_once_with("PLATE-123")
        mock_wait.assert_called_once_with(timeout=120)
    
    @patch.object(EmailSender, 'start_local_server')
    def test_run_email_system_server_fail(self, mock_start):
        """Test email system when server startup fails."""
        mock_start.return_value = False
        
        with patch('builtins.print'):
            result = self.sender.run_email_system("PLATE-456")
        
        self.assertEqual(result, "error")
        mock_start.assert_called_once()
    
    @patch.object(EmailSender, 'start_local_server')
    @patch.object(EmailSender, 'send_vehicle_alert')
    def test_run_email_system_email_fail(self, mock_send, mock_start):
        """Test email system when email sending fails."""
        mock_start.return_value = True
        mock_send.return_value = False
        
        with patch('builtins.print'):
            result = self.sender.run_email_system("PLATE-789")
        
        self.assertEqual(result, "error")
        mock_start.assert_called_once()
        mock_send.assert_called_once_with("PLATE-789")

# EDGE CASE TESTS FOR EMAILSENDER

class TestEmailSenderEdgeCases(unittest.TestCase):
    """Tests for edge cases and boundary conditions of EmailSender."""
    
    def setUp(self):
        self.mock_db = MockDBManager()
        self.sender = EmailSender(self.mock_db)
    
    @patch('smtplib.SMTP')
    def test_empty_license_plate(self, mock_smtp):
        """Test email sending with empty license plate string."""
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        with patch('builtins.print'):
            result = self.sender.send_vehicle_alert("")
        
        self.assertTrue(result)
        self.assertEqual(self.sender.current_plate, "")
    
    @patch('smtplib.SMTP')
    def test_special_characters_plate(self, mock_smtp):
        """Test email sending with special characters in license plate."""
        special_plate = "AB-123-ÉÈ@"
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        with patch('builtins.print'):
            result = self.sender.send_vehicle_alert(special_plate)
        
        self.assertTrue(result)
        self.assertEqual(self.sender.current_plate, special_plate)
    
    @patch('smtplib.SMTP')
    def test_very_long_plate(self, mock_smtp):
        """Test email sending with very long license plate string."""
        long_plate = "A" * 100
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        with patch('builtins.print'):
            result = self.sender.send_vehicle_alert(long_plate)
        
        self.assertTrue(result)
        self.assertEqual(self.sender.current_plate, long_plate)

# DECISION SCENARIO TESTS

class TestEmailSenderDecisionScenarios(unittest.TestCase):
    """Comprehensive tests for all decision scenarios."""
    
    def setUp(self):
        self.mock_db = MockDBManager()
        self.sender = EmailSender(self.mock_db)
    
    def test_all_decision_scenarios(self):
        """Test all possible decision scenarios in cleanup_system."""
        # Define test cases: (decision, should_shutdown, should_exit)
        test_cases = [
            ('accept_whitelist', True, True),    # Normal case: shutdown and exit
            ('accept_only', True, True),         # Normal case: shutdown and exit
            ('reject_blacklist', True, True),    # Normal case: shutdown and exit
            ('reject_only', False, False),       # Special case: early return, no shutdown/exit
            ('unknown', True, True),             # Unknown decision: shutdown and exit
        ]
        
        for decision, should_shutdown, should_exit in test_cases:
            with self.subTest(decision=decision):
                # Reset sender state for each test case
                self.sender = EmailSender(self.mock_db)
                self.sender.decision = decision
                self.sender.current_plate = f"TEST-{decision}"
                self.sender.server = MagicMock()
                self.sender._should_exit = False
                
                with patch('builtins.print'):
                    self.sender.cleanup_system()
                
                if should_shutdown:
                    self.sender.server.shutdown.assert_called_once()
                else:
                    self.sender.server.shutdown.assert_not_called()
                
                if should_exit:
                    self.assertTrue(self.sender._should_exit)
                else:
                    self.assertFalse(self.sender._should_exit)

# CUSTOM TEST RUNNER

class CustomTestResult(unittest.TextTestResult):
    """Custom test result class for enhanced test output."""
    
    def startTest(self, test):
        """Called when a test starts."""
        super().startTest(test)
        test_name = self.getDescription(test)
        print(f"\nStarting test: {test_name}")
    
    def addSuccess(self, test):
        """Called when a test succeeds."""
        super().addSuccess(test)
        test_name = self.getDescription(test)
        print(f"  TEST PASSED: {test_name}")
    
    def addFailure(self, test, err):
        """Called when a test fails."""
        super().addFailure(test, err)
        test_name = self.getDescription(test)
        print(f"  TEST FAILED: {test_name}")
        print(f"    Error: {err[1]}")
    
    def addError(self, test, err):
        """Called when a test encounters an error."""
        super().addError(test, err)
        test_name = self.getDescription(test)
        print(f"  TEST ERROR: {test_name}")
        print(f"    Exception: {err[1]}")

class CustomTestRunner(unittest.TextTestRunner):
    """Custom test runner with enhanced output formatting."""
    
    resultclass = CustomTestResult
    
    def run(self, test):
        """Run the given test case or test suite with custom formatting."""
        print("=" * 70)
        print("UNIT TEST EXECUTION - EmailSender")
        print("=" * 70)
        
        result = super().run(test)
        
        # Print summary
        print("\n" + "=" * 70)
        print("TEST RESULTS SUMMARY")
        print("=" * 70)
        print(f"Tests executed: {result.testsRun}")
        print(f"Tests passed: {result.testsRun - len(result.failures) - len(result.errors)}")
        print(f"Tests failed: {len(result.failures)}")
        print(f"Test errors: {len(result.errors)}")
        
        # Print failure details if any
        if result.failures:
            print("\n" + "-" * 70)
            print("FAILED TEST DETAILS:")
            print("-" * 70)
            for i, (test, traceback) in enumerate(result.failures, 1):
                print(f"\n{i}. {self.getDescription(test)}")
                print(f"   Traceback: {traceback.splitlines()[-1]}")
        
        # Print error details if any
        if result.errors:
            print("\n" + "-" * 70)
            print("TEST ERROR DETAILS:")
            print("-" * 70)
            for i, (test, traceback) in enumerate(result.errors, 1):
                print(f"\n{i}. {self.getDescription(test)}")
                print(f"   Error: {traceback.splitlines()[-1]}")
        
        # Print final status
        print("\n" + "=" * 70)
        if result.wasSuccessful():
            print("ALL TESTS PASSED SUCCESSFULLY!")
        else:
            print("SOME TESTS FAILED OR ENCOUNTERED ERRORS")
        print("=" * 70)
        
        return result
    
    def getDescription(self, test):
        """Get a description of the test for display purposes."""
        return str(test).split()[0]

# TEST EXECUTION FUNCTION

def run_tests():
    """Main function to execute all tests."""
    # Create test loader
    loader = unittest.TestLoader()
    
    # Define all test classes to include
    test_classes = [
        TestEmailSender,
        TestEmailSenderEdgeCases,
        TestEmailSenderDecisionScenarios
    ]
    
    # Build test suite
    suite = unittest.TestSuite()
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Execute tests with custom runner
    runner = CustomTestRunner(verbosity=0)
    result = runner.run(suite)
    
    return result.wasSuccessful()

# MAIN EXECUTION BLOCK

if __name__ == '__main__':
    """
    Entry point for test execution.
    Runs all tests and returns appropriate exit code.
    """
    # Execute tests
    success = run_tests()
    
    # Return exit code (0 for success, 1 for failure)
    exit_code = 0 if success else 1
    exit(exit_code)