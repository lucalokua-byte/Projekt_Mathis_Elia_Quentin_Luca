import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# PATH CONFIGURATION FOR MODULE IMPORT


# Get the absolute path to the 'mail_system' directory containing email_system.py
mail_system_path = r"C:\Python\Project\Projekt_Mathis_Elia_Quentin_Luca\Coding\mail_system"

# Add the mail_system directory to Python's module search path
sys.path.insert(0, mail_system_path)

# Also add the parent directory for additional import flexibility
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# MOCK SETUP FOR EXTERNAL DEPENDENCIES

sys.modules['Interface'] = MagicMock()
sys.modules['Interface.AbstractDBManager'] = MagicMock()

# Define a mock class to simulate the DBManager behavior
class MockDBManager:
    """Mock implementation of DBManager for testing purposes."""
    
    def __init__(self, *args, **kwargs):
        """Initialize mock DBManager (no actual implementation needed)."""
        pass
    
    def whitelist_plate(self, plate):
        """Mock method to whitelist a license plate."""
        print(f"Mock: Whitelisting plate {plate}")
    
    def blacklist_plate(self, plate):
        """Mock method to blacklist a license plate."""
        print(f"Mock: Blacklisting plate {plate}")
    
    def add_license_plate(self, plate, confidence):
        """Mock method to add a license plate with confidence score."""
        print(f"Mock: Adding plate {plate} with confidence {confidence}")
    
    def save_data(self):
        """Mock method to save data."""
        print("Mock: Saving data")

# Replace the actual DBManager module with our mock

sys.modules['Db_maneger'] = MagicMock()
sys.modules['Db_maneger.Db_maneger'] = MagicMock()
sys.modules['Db_maneger.Db_maneger'].DBManager = MockDBManager


from email_system import EmailSender



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
    
    @patch('email_system.smtplib.SMTP')
    def test_send_vehicle_alert_success(self, mock_smtp):
        """Test successful email sending with valid SMTP connection."""
        # Setup mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # Execute the method under test
        result = self.sender.send_vehicle_alert("AB-123-CD")
        
        # Verify the result and state changes
        self.assertTrue(result)
        self.assertEqual(self.sender.current_plate, "AB-123-CD")
        
        # Verify SMTP calls were made correctly
        mock_smtp.assert_called_once_with('smtp.gmail.com', 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with(
            'projetseqlem@gmail.com', 
            'nkab tgue nvqk xkrs'
        )
        mock_server.send_message.assert_called_once()
        mock_server.quit.assert_called_once()
    
    @patch('email_system.smtplib.SMTP')
    def test_send_vehicle_alert_failure(self, mock_smtp):
        """Test email sending failure when SMTP connection fails."""
        # Simulate SMTP connection error
        mock_smtp.side_effect = Exception("SMTP Connection Error")
        
        # Execute the method under test
        result = self.sender.send_vehicle_alert("XY-789-ZZ")
        
        # Verify the method handles failure correctly
        self.assertFalse(result)
        self.assertEqual(self.sender.current_plate, "XY-789-ZZ")
    
    def test_cleanup_system_accept_whitelist(self):
        """Test cleanup system for 'accept_whitelist' decision."""
        # Setup test state
        self.sender.server = MagicMock()
        self.sender.decision = 'accept_whitelist'
        self.sender.current_plate = "TEST-001"
        
        # Execute cleanup
        self.sender.cleanup_system()
        
        # Verify server shutdown and exit flag
        self.sender.server.shutdown.assert_called_once()
        self.assertTrue(self.sender._should_exit)
    
    def test_cleanup_system_accept_only(self):
        """Test cleanup system for 'accept_only' decision."""
        # Setup test state
        self.sender.server = MagicMock()
        self.sender.decision = 'accept_only'
        self.sender.current_plate = "TEST-003"
        
        # Execute cleanup
        self.sender.cleanup_system()
        
        # Verify server shutdown and exit flag
        self.sender.server.shutdown.assert_called_once()
        self.assertTrue(self.sender._should_exit)
    
    def test_cleanup_system_reject_blacklist(self):
        """Test cleanup system for 'reject_blacklist' decision."""
        # Setup test state
        self.sender.server = MagicMock()
        self.sender.decision = 'reject_blacklist'
        self.sender.current_plate = "TEST-004"
        
        # Execute cleanup
        self.sender.cleanup_system()
        
        # Verify server shutdown and exit flag
        self.sender.server.shutdown.assert_called_once()
        self.assertTrue(self.sender._should_exit)
    
    def test_cleanup_system_reject_only(self):
        """Test cleanup system for 'reject_only' decision (early return case)."""
        # Setup test state
        self.sender.server = MagicMock()
        self.sender.decision = 'reject_only'
        self.sender.current_plate = "TEST-002"
        
        # Execute cleanup
        self.sender.cleanup_system()
        
        # IMPORTANT: For 'reject_only', the real code has an early return
        # Server should NOT be shut down in this case
        self.sender.server.shutdown.assert_not_called()
        self.assertFalse(self.sender._should_exit)
    
    def test_cleanup_system_unknown_decision(self):
        """Test cleanup system for unknown decision."""
        # Setup test state
        self.sender.server = MagicMock()
        self.sender.decision = 'unknown_decision'
        self.sender.current_plate = "TEST-005"
        
        # Execute cleanup
        self.sender.cleanup_system()
        
        # Verify server shutdown and exit flag
        self.sender.server.shutdown.assert_called_once()
        self.assertTrue(self.sender._should_exit)
    
    def test_wait_for_decision_with_decision(self):
        """Test waiting for decision when decision is already made."""
        # Set decision before calling wait
        self.sender.decision = 'accept_only'
        
        # Execute wait method
        result = self.sender.wait_for_decision(timeout=1)
        
        # Should return immediately with existing decision
        self.assertEqual(result, 'accept_only')
    
    def test_wait_for_decision_timeout(self):
        """Test waiting for decision timeout when no decision is made."""
        # Execute wait with very short timeout
        result = self.sender.wait_for_decision(timeout=0.1)
        
        # Should return "timeout" when no decision received
        self.assertEqual(result, "timeout")
    
    def test_wait_for_decision_should_exit(self):
        """Test waiting for decision when exit flag is set."""
        # Set exit flag to True
        self.sender._should_exit = True
        
        # Execute wait method
        result = self.sender.wait_for_decision(timeout=5)
        
        # Should return None when exit flag is True
        self.assertIsNone(result)
    
    @patch('email_system.HTTPServer')
    @patch('email_system.threading.Thread')
    def test_start_local_server_success(self, mock_thread, mock_httpserver):
        """Test successful local server startup."""
        # Setup mock objects
        mock_server_instance = MagicMock()
        mock_httpserver.return_value = mock_server_instance
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance
        
        # Execute server startup
        result = self.sender.start_local_server()
        
        # Verify successful startup
        self.assertTrue(result)
        self.assertEqual(self.sender.server, mock_server_instance)
        
        # Verify HTTPServer was called with correct parameters
        mock_httpserver.assert_called_once_with(('localhost', 8080), unittest.mock.ANY)
        
        # Verify thread was created and started
        mock_thread.assert_called_once()
        mock_thread_instance.start.assert_called_once()
        self.assertTrue(mock_thread_instance.daemon)
    
    @patch('email_system.HTTPServer')
    def test_start_local_server_failure(self, mock_httpserver):
        """Test local server startup failure."""
        # Simulate server creation failure
        mock_httpserver.side_effect = Exception("Port 8080 already in use")
        
        # Execute server startup (should fail)
        result = self.sender.start_local_server()
        
        # Verify failure is handled correctly
        self.assertFalse(result, "start_local_server() should return False on error")
        self.assertIsNone(self.sender.server)
    
    @patch.object(EmailSender, 'start_local_server')
    @patch.object(EmailSender, 'send_vehicle_alert')
    @patch.object(EmailSender, 'wait_for_decision')
    def test_run_email_system_success(self, mock_wait, mock_send, mock_start):
        """Test complete email system execution with success."""
        # Setup mock return values
        mock_start.return_value = True
        mock_send.return_value = True
        mock_wait.return_value = 'accept_whitelist'
        
        # Execute complete system
        result = self.sender.run_email_system("PLATE-123")
        
        # Verify result and method calls
        self.assertEqual(result, 'accept_whitelist')
        mock_start.assert_called_once()
        mock_send.assert_called_once_with("PLATE-123")
        mock_wait.assert_called_once_with(timeout=120)
    
    @patch.object(EmailSender, 'start_local_server')
    def test_run_email_system_server_fail(self, mock_start):
        """Test email system when server startup fails."""
        # Simulate server startup failure
        mock_start.return_value = False
        
        # Execute system
        result = self.sender.run_email_system("PLATE-456")
        
        # Should return "error"
        self.assertEqual(result, "error")
        mock_start.assert_called_once()
    
    @patch.object(EmailSender, 'start_local_server')
    @patch.object(EmailSender, 'send_vehicle_alert')
    def test_run_email_system_email_fail(self, mock_send, mock_start):
        """Test email system when email sending fails."""
        # Server starts successfully but email fails
        mock_start.return_value = True
        mock_send.return_value = False
        
        # Execute system
        result = self.sender.run_email_system("PLATE-789")
        
        # Should return "error"
        self.assertEqual(result, "error")
        mock_start.assert_called_once()
        mock_send.assert_called_once_with("PLATE-789")


# EDGE CASE TESTS FOR EMAILSENDER


class TestEmailSenderEdgeCases(unittest.TestCase):
    """Tests for edge cases and boundary conditions of EmailSender."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_db = MockDBManager()
        self.sender = EmailSender(self.mock_db)
    
    @patch('email_system.smtplib.SMTP')
    def test_empty_license_plate(self, mock_smtp):
        """Test email sending with empty license plate string."""
        # Setup mock SMTP
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # Execute with empty plate
        result = self.sender.send_vehicle_alert("")
        
        # Should succeed and store empty string
        self.assertTrue(result)
        self.assertEqual(self.sender.current_plate, "")
    
    @patch('email_system.smtplib.SMTP')
    def test_special_characters_plate(self, mock_smtp):
        """Test email sending with special characters in license plate."""
        # Plate with special characters
        special_plate = "AB-123-ÉÈ@"
        
        # Setup mock SMTP
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # Execute with special plate
        result = self.sender.send_vehicle_alert(special_plate)
        
        # Should succeed and store special characters
        self.assertTrue(result)
        self.assertEqual(self.sender.current_plate, special_plate)
    
    @patch('email_system.smtplib.SMTP')
    def test_very_long_plate(self, mock_smtp):
        """Test email sending with very long license plate string."""
        # Create extremely long plate
        long_plate = "A" * 100
        
        # Setup mock SMTP
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # Execute with long plate
        result = self.sender.send_vehicle_alert(long_plate)
        
        # Should succeed and store long string
        self.assertTrue(result)
        self.assertEqual(self.sender.current_plate, long_plate)


# DECISION SCENARIO TESTS

class TestEmailSenderDecisionScenarios(unittest.TestCase):
    """Comprehensive tests for all decision scenarios."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
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
                self.mock_db = MockDBManager()
                self.sender.db = self.mock_db
                self.sender.decision = decision
                self.sender.current_plate = f"TEST-{decision}"
                self.sender.server = MagicMock()
                self.sender._should_exit = False
                
                # Execute cleanup
                self.sender.cleanup_system()
                
                # Verify server shutdown behavior
                if should_shutdown:
                    self.sender.server.shutdown.assert_called_once()
                else:
                    self.sender.server.shutdown.assert_not_called()
                
                # Verify exit flag behavior
                if should_exit:
                    self.assertTrue(self.sender._should_exit)
                else:
                    self.assertFalse(self.sender._should_exit)



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
        print("Following Python Testing course principles")
        print("=" * 70)
        
        # Run tests using parent class
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