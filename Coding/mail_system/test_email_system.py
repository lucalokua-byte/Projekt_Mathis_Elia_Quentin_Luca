import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Ajouter le chemin parent pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock les modules problématiques avant l'import
sys.modules['Interface'] = MagicMock()
sys.modules['Interface.AbstractDBManager'] = MagicMock()

# Créer un mock pour DBManager
class MockDBManager:
    def __init__(self, *args, **kwargs):
        pass
    
    def whitelist_plate(self, plate):
        print(f"Mock: Whitelisting plate {plate}")
    
    def blacklist_plate(self, plate):
        print(f"Mock: Blacklisting plate {plate}")
    
    def add_license_plate(self, plate, confidence):
        print(f"Mock: Adding plate {plate} with confidence {confidence}")
    
    def save_data(self):
        print("Mock: Saving data")

# Remplacer DBManager par notre mock
sys.modules['Db_maneger'] = MagicMock()
sys.modules['Db_maneger.Db_maneger'] = MagicMock()
sys.modules['Db_maneger.Db_maneger'].DBManager = MockDBManager

# Maintenant importer le module à tester
from email_system import EmailSender


class TestEmailSender(unittest.TestCase):
    """Tests unitaires pour la classe EmailSender."""
    
    def setUp(self):
        """Préparation avant chaque test."""
        self.mock_db = MockDBManager()
        self.sender = EmailSender(self.mock_db)
    
    def test_initialization(self):
        """Test de l'initialisation de la classe."""
        self.assertEqual(self.sender.gmail_config['email'], 'projetseqlem@gmail.com')
        self.assertEqual(self.sender.gmail_config['smtp_server'], 'smtp.gmail.com')
        self.assertEqual(self.sender.gmail_config['smtp_port'], 587)
        self.assertIsNone(self.sender.decision)
        self.assertIsNone(self.sender.current_plate)
        self.assertIsNone(self.sender.server)
        self.assertFalse(self.sender._should_exit)
        self.assertEqual(self.sender.db, self.mock_db)
    
    @patch('email_system.smtplib.SMTP')
    def test_send_vehicle_alert_success(self, mock_smtp):
        """Test d'envoi d'email réussi."""
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        result = self.sender.send_vehicle_alert("AB-123-CD")
        
        self.assertTrue(result)
        self.assertEqual(self.sender.current_plate, "AB-123-CD")
        
        # Vérifier les appels SMTP
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
        """Test d'échec d'envoi d'email."""
        mock_smtp.side_effect = Exception("SMTP Connection Error")
        
        result = self.sender.send_vehicle_alert("XY-789-ZZ")
        
        self.assertFalse(result)
        self.assertEqual(self.sender.current_plate, "XY-789-ZZ")
    
    def test_cleanup_system_accept_whitelist(self):
        """Test pour accept_whitelist."""
        self.sender.server = MagicMock()
        self.sender.decision = 'accept_whitelist'
        self.sender.current_plate = "TEST-001"
        
        self.sender.cleanup_system()
        
        # Pour accept_whitelist, tout devrait être appelé
        self.sender.server.shutdown.assert_called_once()
        self.assertTrue(self.sender._should_exit)
    
    def test_cleanup_system_accept_only(self):
        """Test pour accept_only."""
        self.sender.server = MagicMock()
        self.sender.decision = 'accept_only'
        self.sender.current_plate = "TEST-003"
        
        self.sender.cleanup_system()
        
        # Pour accept_only, tout devrait être appelé
        self.sender.server.shutdown.assert_called_once()
        self.assertTrue(self.sender._should_exit)
    
    def test_cleanup_system_reject_blacklist(self):
        """Test pour reject_blacklist."""
        self.sender.server = MagicMock()
        self.sender.decision = 'reject_blacklist'
        self.sender.current_plate = "TEST-004"
        
        self.sender.cleanup_system()
        
        # Pour reject_blacklist, tout devrait être appelé
        self.sender.server.shutdown.assert_called_once()
        self.assertTrue(self.sender._should_exit)
    
    def test_cleanup_system_reject_only(self):
        """Test spécifique pour reject_only (cas spécial avec return précoce)."""
        self.sender.server = MagicMock()
        self.sender.decision = 'reject_only'
        self.sender.current_plate = "TEST-002"
        
        self.sender.cleanup_system()
        
        # IMPORTANT: Pour reject_only, il y a un return précoce dans le code
        # Donc server.shutdown() NE DEVRAIT PAS être appelé !
        self.sender.server.shutdown.assert_not_called()
        # _should_exit ne devrait pas être défini à True
        self.assertFalse(self.sender._should_exit)
    
    def test_cleanup_system_unknown_decision(self):
        """Test pour une décision inconnue."""
        self.sender.server = MagicMock()
        self.sender.decision = 'unknown_decision'
        self.sender.current_plate = "TEST-005"
        
        self.sender.cleanup_system()
        
        # Pour une décision inconnue, tout devrait être appelé
        self.sender.server.shutdown.assert_called_once()
        self.assertTrue(self.sender._should_exit)
    
    def test_wait_for_decision_with_decision(self):
        """Test d'attente avec décision déjà prise."""
        self.sender.decision = 'accept_only'
        
        result = self.sender.wait_for_decision(timeout=1)
        
        self.assertEqual(result, 'accept_only')
    
    def test_wait_for_decision_timeout(self):
        """Test d'expiration du timeout."""
        result = self.sender.wait_for_decision(timeout=0.1)  # Timeout très court
        
        self.assertEqual(result, "timeout")
    
    def test_wait_for_decision_should_exit(self):
        """Test d'attente avec flag d'arrêt."""
        self.sender._should_exit = True
        
        result = self.sender.wait_for_decision(timeout=5)
        
        # Selon le code, si _should_exit est True, retourne self.decision (qui est None)
        self.assertIsNone(result)
    
    @patch('email_system.HTTPServer')
    @patch('email_system.threading.Thread')
    def test_start_local_server_success(self, mock_thread, mock_httpserver):
        """Test de démarrage réussi du serveur."""
        mock_server_instance = MagicMock()
        mock_httpserver.return_value = mock_server_instance
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance
        
        result = self.sender.start_local_server()
        
        self.assertTrue(result)
        self.assertIsNotNone(self.sender.server)
        mock_httpserver.assert_called_once()
        mock_thread.assert_called_once()
        mock_thread_instance.start.assert_called_once()
        self.assertTrue(mock_thread_instance.daemon)
    
    @patch('email_system.HTTPServer')
    def test_start_local_server_failure(self, mock_httpserver):
        """Test d'échec du démarrage du serveur."""
        mock_httpserver.side_effect = Exception("Port 8080 already in use")
        
        result = self.sender.start_local_server()
        
        self.assertFalse(result)
        self.assertIsNone(self.sender.server)
    
    @patch.object(EmailSender, 'start_local_server')
    @patch.object(EmailSender, 'send_vehicle_alert')
    @patch.object(EmailSender, 'wait_for_decision')
    def test_run_email_system_success(self, mock_wait, mock_send, mock_start):
        """Test du système complet avec succès."""
        mock_start.return_value = True
        mock_send.return_value = True
        mock_wait.return_value = 'accept_whitelist'
        
        result = self.sender.run_email_system("PLATE-123")
        
        self.assertEqual(result, 'accept_whitelist')
        mock_start.assert_called_once()
        mock_send.assert_called_once_with("PLATE-123")
        mock_wait.assert_called_once_with(timeout=120)
    
    @patch.object(EmailSender, 'start_local_server')
    def test_run_email_system_server_fail(self, mock_start):
        """Test d'échec au démarrage du serveur."""
        mock_start.return_value = False
        
        result = self.sender.run_email_system("PLATE-456")
        
        self.assertEqual(result, "error")
        mock_start.assert_called_once()
    
    @patch.object(EmailSender, 'start_local_server')
    @patch.object(EmailSender, 'send_vehicle_alert')
    def test_run_email_system_email_fail(self, mock_send, mock_start):
        """Test d'échec à l'envoi de l'email."""
        mock_start.return_value = True
        mock_send.return_value = False
        
        result = self.sender.run_email_system("PLATE-789")
        
        self.assertEqual(result, "error")
        mock_start.assert_called_once()
        mock_send.assert_called_once_with("PLATE-789")


class TestEmailSenderEdgeCases(unittest.TestCase):
    """Tests des cas limites pour EmailSender."""
    
    def setUp(self):
        self.mock_db = MockDBManager()
        self.sender = EmailSender(self.mock_db)
    
    def test_empty_license_plate(self):
        """Test avec une plaque d'immatriculation vide."""
        with patch('email_system.smtplib.SMTP') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value = mock_server
            
            result = self.sender.send_vehicle_alert("")
            
            self.assertTrue(result)
            self.assertEqual(self.sender.current_plate, "")
    
    def test_special_characters_plate(self):
        """Test avec des caractères spéciaux dans la plaque."""
        special_plate = "AB-123-ÉÈ@"
        with patch('email_system.smtplib.SMTP') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value = mock_server
            
            result = self.sender.send_vehicle_alert(special_plate)
            
            self.assertTrue(result)
            self.assertEqual(self.sender.current_plate, special_plate)
    
    def test_very_long_plate(self):
        """Test avec une plaque très longue."""
        long_plate = "A" * 100
        with patch('email_system.smtplib.SMTP') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value = mock_server
            
            result = self.sender.send_vehicle_alert(long_plate)
            
            self.assertTrue(result)
            self.assertEqual(self.sender.current_plate, long_plate)


class TestEmailSenderDecisionScenarios(unittest.TestCase):
    """Tests pour tous les scénarios de décision."""
    
    def setUp(self):
        self.mock_db = MockDBManager()
        self.sender = EmailSender(self.mock_db)
    
    def test_all_decision_scenarios(self):
        """Test toutes les décisions possibles."""
        test_cases = [
            ('accept_whitelist', True, True),    # server shutdown, _should_exit
            ('accept_only', True, True),         # server shutdown, _should_exit
            ('reject_blacklist', True, True),    # server shutdown, _should_exit
            ('reject_only', False, False),       # NO server shutdown (return précoce), NO _should_exit
            ('unknown', True, True),             # server shutdown, _should_exit
        ]
        
        for decision, should_shutdown, should_exit in test_cases:
            with self.subTest(decision=decision):
                # Réinitialiser
                self.mock_db = MockDBManager()
                self.sender.db = self.mock_db
                self.sender.decision = decision
                self.sender.current_plate = f"TEST-{decision}"
                self.sender.server = MagicMock()
                self.sender._should_exit = False  # Réinitialiser
                
                # Exécuter cleanup
                self.sender.cleanup_system()
                
                # Vérifier les appels
                if should_shutdown:
                    self.sender.server.shutdown.assert_called_once()
                else:
                    self.sender.server.shutdown.assert_not_called()
                
                # Vérifier _should_exit
                if should_exit:
                    self.assertTrue(self.sender._should_exit)
                else:
                    self.assertFalse(self.sender._should_exit)


class CustomTestResult(unittest.TextTestResult):
    """Classe personnalisée pour afficher les résultats de test."""
    
    def startTest(self, test):
        super().startTest(test)
        test_name = self.getDescription(test)
        print(f"\n▶ Début du test: {test_name}")
    
    def addSuccess(self, test):
        super().addSuccess(test)
        test_name = self.getDescription(test)
        print(f"  ✓ TEST RÉUSSI: {test_name}")
    
    def addFailure(self, test, err):
        super().addFailure(test, err)
        test_name = self.getDescription(test)
        print(f"  ✗ TEST ÉCHOUÉ: {test_name}")
        print(f"    Erreur: {err[1]}")
    
    def addError(self, test, err):
        super().addError(test, err)
        test_name = self.getDescription(test)
        print(f"  ⚠ ERREUR DE TEST: {test_name}")
        print(f"    Exception: {err[1]}")


class CustomTestRunner(unittest.TextTestRunner):
    """Runner personnalisé pour les tests."""
    
    resultclass = CustomTestResult
    
    def run(self, test):
        print("=" * 70)
        print("EXÉCUTION DES TESTS UNITAIRES - EmailSender")
        print("Suivi des principes du cours Python Testing")
        print("=" * 70)
        
        result = super().run(test)
        
        print("\n" + "=" * 70)
        print("RÉSUMÉ DES RÉSULTATS")
        print("=" * 70)
        print(f"Tests exécutés: {result.testsRun}")
        print(f"Tests réussis: {result.testsRun - len(result.failures) - len(result.errors)}")
        print(f"Tests échoués: {len(result.failures)}")
        print(f"Erreurs de test: {len(result.errors)}")
        
        if result.failures:
            print("\n" + "-" * 70)
            print("DÉTAILS DES TESTS ÉCHOUÉS:")
            print("-" * 70)
            for i, (test, traceback) in enumerate(result.failures, 1):
                print(f"\n{i}. {self.getDescription(test)}")
                print(f"   Traceback: {traceback.splitlines()[-1]}")
        
        if result.errors:
            print("\n" + "-" * 70)
            print("DÉTAILS DES ERREURS DE TEST:")
            print("-" * 70)
            for i, (test, traceback) in enumerate(result.errors, 1):
                print(f"\n{i}. {self.getDescription(test)}")
                print(f"   Erreur: {traceback.splitlines()[-1]}")
        
        print("\n" + "=" * 70)
        if result.wasSuccessful():
            print("✅ TOUS LES TESTS ONT RÉUSSI !")
        else:
            print("❌ CERTAINS TESTS ONT ÉCHOUÉ OU PROVOQUÉ DES ERREURS")
        print("=" * 70)
        
        return result
    
    def getDescription(self, test):
        """Récupère la description du test."""
        return str(test).split()[0]


def run_tests():
    """Fonction principale pour exécuter les tests."""
    # Charger tous les tests
    loader = unittest.TestLoader()
    
    # Créer une suite de tests avec toutes les classes de test
    test_classes = [
        TestEmailSender,
        TestEmailSenderEdgeCases,
        TestEmailSenderDecisionScenarios
    ]
    
    suite = unittest.TestSuite()
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Exécuter les tests avec notre runner personnalisé
    runner = CustomTestRunner(verbosity=0)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    # Exécuter les tests avec notre système personnalisé
    success = run_tests()
    
    # Retourner le code d'erreur approprié
    exit_code = 0 if success else 1
    exit(exit_code)