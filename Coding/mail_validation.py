import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

class EmailSender:
    """
    Programme simple pour envoyer des emails via Gmail
    """

    def __init__(self):  # ⚠️ CORRIGÉ : __init__ avec DEUX underscores
        # CONFIGURATION À ADAPTER
        self.gmail_config = {
            'email': 'projetseqlem@gmail.com',
            'app_password': 'nkab tgue nvqk xkrs',   # Mot de passe d'application
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587
        }

    def send_vehicle_alert(self, plate_number: str, recipient_email: str = None):

        if recipient_email is None:
            recipient_email = self.gmail_config['email']
        
        try:
            print("📧 Préparation de l'email...")
            
            subject = f"🚗 Véhicule inconnu détecté - {plate_number}"
            body = self._create_email_body(plate_number)
            
            msg = MIMEMultipart()
            msg['From'] = self.gmail_config['email']
            msg['To'] = recipient_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            print("🔗 Connexion à Gmail...")
            server = smtplib.SMTP(self.gmail_config['smtp_server'], self.gmail_config['smtp_port'])
            server.starttls()
            server.login(self.gmail_config['email'], self.gmail_config['app_password'])
            
            print("✈️ Envoi de l'email...")
            server.send_message(msg)
            server.quit()
            
            print(f"✅ Email envoyé avec succès à {recipient_email}")

        except smtplib.SMTPAuthenticationError as e:
            print("❌ ERREUR: Échec de l'authentification Gmail")
            print("→ Vérifiez le mot de passe d'application et le 2FA")
            print(e)
        except Exception as e:
            print(f"❌ Erreur lors de l'envoi: {str(e)}")

    def _create_email_body(self, plate_number: str) -> str:
        current_time = datetime.now().strftime("%d/%m/%Y à %H:%M:%S")
        
        return f"""
ALERTE SÉCURITÉ - VÉHICULE INCONNU

Plaque : {plate_number}
Date : {current_time}

Ce message a été généré automatiquement.
"""

    def test_connection(self):
        try:
            server = smtplib.SMTP(self.gmail_config['smtp_server'], self.gmail_config['smtp_port'])
            server.starttls()
            server.login(self.gmail_config['email'], self.gmail_config['app_password'])
            server.quit()
            print("✅ Connexion Gmail réussie!")
            return True
        except Exception as e:
            print(f"❌ Erreur de connexion: {e}")
            return False


# -----------------------------------------------------

def main():
    print("🚗 SYSTÈME D'ALERTE EMAIL")
    print("=" * 40)
    
    sender = EmailSender()
    
    print("1. Test de connexion Gmail...")
    if sender.test_connection():
        print("2. Envoi de l'alerte...")
        sender.send_vehicle_alert("AB-123-CD")
    else:
        print("❌ Impossible de continuer sans connexion Gmail valide.")

# -----------------------------------------------------

if __name__ == "__main__":  # ⚠️ CORRIGÉ : __main__ avec DEUX underscores
    main()