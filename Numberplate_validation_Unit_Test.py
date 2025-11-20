import unittest
from unittest.mock import patch
from io import StringIO
import sys
import os

# Add the parent directory to the path to import the module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Coding.Numberplate_validation import UnknownPlateHandler

class TestUnknownPlateHandler(unittest.TestCase):
    """
    Unit tests for UnknownPlateHandler class
    Tests alarm notification and manual approval/rejection logic
    """
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.handler = UnknownPlateHandler()
        self.test_plate = "AB-123-CD"
    
    def test_initialization(self):
        """Test that handler initializes correctly"""
        self.assertIsInstance(self.handler, UnknownPlateHandler)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_send_alarm_notification(self, mock_stdout):
        """Test that alarm notification prints correct message"""
        self.handler._send_alarm_notification(self.test_plate)
        
        output = mock_stdout.getvalue()
        self.assertIn("ALARM: Unknown license plate detected", output)
        self.assertIn(self.test_plate, output)
        self.assertIn("Notification sent to owner...", output)
    
    @patch('builtins.input', return_value='1')
    @patch('sys.stdout', new_callable=StringIO)
    def test_get_owner_decision_allow(self, mock_stdout, mock_input):
        """Test owner decision when allowing access"""
        decision = self.handler._get_owner_decision(self.test_plate)
        
        self.assertEqual(decision, 'ALLOW')
        
        output = mock_stdout.getvalue()
        self.assertIn("Unrecognized vehicle - License plate:", output)
        self.assertIn(self.test_plate, output)
        self.assertIn("Grant access", output)
        self.assertIn("Deny access", output)
    
    @patch('builtins.input', return_value='2')
    @patch('sys.stdout', new_callable=StringIO)
    def test_get_owner_decision_deny(self, mock_stdout, mock_input):
        """Test owner decision when denying access"""
        decision = self.handler._get_owner_decision(self.test_plate)
        
        self.assertEqual(decision, 'DENY')
        
        output = mock_stdout.getvalue()
        self.assertIn("Deny access", output)
    
    @patch('builtins.input', side_effect=['3', 'invalid', '1'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_get_owner_decision_invalid_then_valid(self, mock_stdout, mock_input):
        """Test handling of invalid input followed by valid input"""
        decision = self.handler._get_owner_decision(self.test_plate)
        
        self.assertEqual(decision, 'ALLOW')
        
        output = mock_stdout.getvalue()
        self.assertIn("Invalid choice. Please enter 1 to ALLOW or 2 to DENY.", output)
    
    @patch('builtins.input', side_effect=KeyboardInterrupt)
    @patch('sys.stdout', new_callable=StringIO)
    def test_get_owner_decision_keyboard_interrupt(self, mock_stdout, mock_input):
        """Test that keyboard interrupt results in denied access"""
        decision = self.handler._get_owner_decision(self.test_plate)
        
        self.assertEqual(decision, 'DENY')
        
        output = mock_stdout.getvalue()
        self.assertIn("Interruption detected. Access denied for security reasons.", output)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_process_decision_allow(self, mock_stdout):
        """Test processing ALLOW decision"""
        result = self.handler._process_decision('ALLOW', self.test_plate)
        
        self.assertTrue(result)
        
        output = mock_stdout.getvalue()
        self.assertIn("Access GRANTED for license plate:", output)
        self.assertIn(self.test_plate, output)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_process_decision_deny(self, mock_stdout):
        """Test processing DENY decision"""
        result = self.handler._process_decision('DENY', self.test_plate)
        
        self.assertFalse(result)
        
        output = mock_stdout.getvalue()
        self.assertIn("Access DENIED for license plate:", output)
        self.assertIn(self.test_plate, output)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_process_decision_invalid_default_deny(self, mock_stdout):
        """Test that invalid decision defaults to DENY"""
        result = self.handler._process_decision('INVALID', self.test_plate)
        
        self.assertFalse(result)
        
        output = mock_stdout.getvalue()
        self.assertIn("Access DENIED for license plate:", output)
        self.assertIn(self.test_plate, output)
    
    @patch.object(UnknownPlateHandler, '_send_alarm_notification')
    @patch.object(UnknownPlateHandler, '_get_owner_decision')
    @patch.object(UnknownPlateHandler, '_process_decision')
    def test_handle_unknown_plate_integration(self, mock_process, mock_decision, mock_alarm):
        """Test the complete handle_unknown_plate method integration"""
        # Setup mocks
        mock_decision.return_value = 'ALLOW'
        mock_process.return_value = True
        
        # Execute the main method
        result = self.handler.handle_unknown_plate(self.test_plate)
        
        # Verify all methods were called correctly
        mock_alarm.assert_called_once_with(self.test_plate)
        mock_decision.assert_called_once_with(self.test_plate)
        mock_process.assert_called_once_with('ALLOW', self.test_plate)
        
        self.assertTrue(result)
    
    @patch.object(UnknownPlateHandler, '_send_alarm_notification')
    @patch.object(UnknownPlateHandler, '_get_owner_decision')
    @patch.object(UnknownPlateHandler, '_process_decision')
    def test_handle_unknown_plate_deny_flow(self, mock_process, mock_decision, mock_alarm):
        """Test the complete flow when access is denied"""
        # Setup mocks for deny flow
        mock_decision.return_value = 'DENY'
        mock_process.return_value = False
        
        # Execute the main method
        result = self.handler.handle_unknown_plate(self.test_plate)
        
        # Verify all methods were called correctly
        mock_alarm.assert_called_once_with(self.test_plate)
        mock_decision.assert_called_once_with(self.test_plate)
        mock_process.assert_called_once_with('DENY', self.test_plate)
        
        self.assertFalse(result)
    
    @patch('builtins.input', return_value='1')
    @patch('sys.stdout', new_callable=StringIO)
    def test_complete_workflow_allow(self, mock_stdout, mock_input):
        """Test complete workflow with ALLOW decision"""
        result = self.handler.handle_unknown_plate(self.test_plate)
        
        self.assertTrue(result)
        
        output = mock_stdout.getvalue()
        # Verify all expected outputs are present
        self.assertIn("ALARM: Unknown license plate detected:", output)
        self.assertIn("Unrecognized vehicle - License plate:", output)
        self.assertIn("Access GRANTED for license plate:", output)
    
    @patch('builtins.input', return_value='2')
    @patch('sys.stdout', new_callable=StringIO)
    def test_complete_workflow_deny(self, mock_stdout, mock_input):
        """Test complete workflow with DENY decision"""
        result = self.handler.handle_unknown_plate(self.test_plate)
        
        self.assertFalse(result)
        
        output = mock_stdout.getvalue()
        self.assertIn("Access DENIED for license plate:", output)


class TestUnknownPlateHandlerEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""
    
    def setUp(self):
        self.handler = UnknownPlateHandler()
    
    @patch('builtins.input', return_value='1')
    @patch('sys.stdout', new_callable=StringIO)
    def test_empty_license_plate(self, mock_stdout, mock_input):
        """Test behavior with empty license plate string"""
        empty_plate = ""
        
        result = self.handler.handle_unknown_plate(empty_plate)
        
        output = mock_stdout.getvalue()
        self.assertIn("ALARM: Unknown license plate detected:", output)
        self.assertIn("Unrecognized vehicle - License plate:", output)
        self.assertTrue(result)
    
    @patch('builtins.input', return_value='2')
    @patch('sys.stdout', new_callable=StringIO)
    def test_special_characters_license_plate(self, mock_stdout, mock_input):
        """Test behavior with special characters in license plate"""
        special_plate = "AB-123-@#$"
        
        result = self.handler.handle_unknown_plate(special_plate)
        
        output = mock_stdout.getvalue()
        self.assertIn("ALARM: Unknown license plate detected:", output)
        self.assertIn(special_plate, output)
        self.assertFalse(result)


if __name__ == '__main__':
    # Create a test suite with all tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestUnknownPlateHandler))
    suite.addTests(loader.loadTestsFromTestCase(TestUnknownPlateHandlerEdgeCases))
    
    # Run the tests with custom result display
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    # Custom output format
    print("\n" + "=" * 50)
    print(f"Ran {result.testsRun} tests in {result.testsRun * 0.001:.3f}s")  # Simulated time
    
    if result.failures or result.errors:
        print(f"FAILED (failures={len(result.failures)})")
    else:
        print("OK")
    
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success: {result.wasSuccessful()}")