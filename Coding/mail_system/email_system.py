import smtplib
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import time
import sys

class EmailSender:
    """
    Main class that handles email sending and decision processing for vehicle security system.
    This system sends an email with 4 action buttons when an unknown vehicle is detected.
    """
    
    def __init__(self):
        """Initialize the EmailSender with Gmail configuration and state variables."""
        # Gmail SMTP configuration for sending emails
        self.gmail_config = {
            'email': 'projetseqlem@gmail.com',
            'app_password': 'nkab tgue nvqk xkrs',  # App-specific password for Gmail
            'smtp_server': 'smtp.gmail.com',        # Gmail's SMTP server address
            'smtp_port': 587                         # Gmail's SMTP port for TLS
        }
        self.decision = None        # Stores the user's decision from email buttons
        self.current_plate = None   # Stores the currently detected license plate
        self.server = None          # Reference to the HTTP server instance
        self._should_exit = False   # New flag to control exit behavior

    def send_vehicle_alert(self, plate_number: str):
        """
        Send an HTML email with 4 action buttons when an unknown vehicle is detected.
        
        Args:
            plate_number (str): The detected vehicle's license plate number
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            print("Sending email with 4 buttons...")
            
            # Store the plate number for later reference
            self.current_plate = plate_number
            # Get current timestamp for the alert
            current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            
            # Create HTML email content with 4 action buttons
            subject = f"Vehicle {plate_number} detected"
            html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <div style="background: #2c3e50; padding: 20px; color: white; text-align: center;">
        <h1>UNKNOWN VEHICLE DETECTED</h1>
    </div>
    
    <div style="padding: 20px; background: #f8f9fa;">
        <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h2>Vehicle information</h2>
            <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #eee; font-weight: bold;">License plate :</td>
                    <td style="padding: 10px; border-bottom: 1px solid #eee; font-size: 18px; color: #333;">{plate_number}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #eee; font-weight: bold;">Date and time :</td>
                    <td style="padding: 10px; border-bottom: 1px solid #eee;">{current_time}</td>
                </tr>
            </table>
            
            <div style="margin: 30px 0; text-align: center;">
                <h3>CHOOSE AN ACTION :</h3>
                
                <!-- Line 1: ACCEPT buttons - Green colored buttons for granting access -->
                <div style="display: flex; justify-content: center; gap: 15px; margin: 20px 0; flex-wrap: wrap;">
                    <a href="http://localhost:8080/accept_whitelist" 
                       style="background: #27ae60; color: white; padding: 12px 20px; text-decoration: none; 
                              border-radius: 8px; font-size: 14px; font-weight: bold; display: inline-block;
                              box-shadow: 0 4px 6px rgba(0,0,0,0.1); min-width: 200px; text-align: center;">
                       ✅ ACCEPT<br>
                       <small>+ Add to Whitelist</small>
                    </a>
                    
                    <a href="http://localhost:8080/accept_only" 
                       style="background: #2ecc71; color: white; padding: 12px 20px; text-decoration: none; 
                              border-radius: 8px; font-size: 14px; font-weight: bold; display: inline-block;
                              box-shadow: 0 4px 6px rgba(0,0,0,0.1); min-width: 200px; text-align: center;">
                       ✅ ACCEPT<br>
                       <small>Without Whitelist</small>
                    </a>
                </div>
                
                <!-- Line 2: REJECT buttons - Red colored buttons for denying access -->
                <div style="display: flex; justify-content: center; gap: 15px; margin: 20px 0; flex-wrap: wrap;">
                    <a href="http://localhost:8080/reject_blacklist" 
                       style="background: #c0392b; color: white; padding: 12px 20px; text-decoration: none; 
                              border-radius: 8px; font-size: 14px; font-weight: bold; display: inline-block;
                              box-shadow: 0 4px 6px rgba(0,0,0,0.1); min-width: 200px; text-align: center;">
                       ❌ REJECT<br>
                       <small>+ Add to Blacklist</small>
                    </a>
                    
                    <a href="http://localhost:8080/reject_only" 
                       style="background: #e74c3c; color: white; padding: 12px 20px; text-decoration: none; 
                              border-radius: 8px; font-size: 14px; font-weight: bold; display: inline-block;
                              box-shadow: 0 4px 6px rgba(0,0,0,0.1); min-width: 200px; text-align: center;">
                       ❌ REJECT<br>
                       <small>Without Blacklist</small>
                    </a>
                </div>
                
                <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 20px;">
                    <p style="color: #666; font-size: 14px; margin: 0;">
                        <strong>Whitelist:</strong> Vehicle will always be accepted in the future<br>
                        <strong>Blacklist:</strong> Vehicle will always be rejected in the future
                    </p>
                </div>
            </div>
        </div>
    </div>
    
    <div style="text-align: center; padding: 20px; color: #666; font-size: 12px;">
        <p>Automatic security system - {current_time}</p>
    </div>
</body>
</html>
"""
            # Create MIME multipart message for HTML email
            msg = MIMEMultipart()
            msg['From'] = self.gmail_config['email']
            msg['To'] = self.gmail_config['email']
            msg['Subject'] = subject
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))
            
            # Connect to SMTP server and send email
            server = smtplib.SMTP(self.gmail_config['smtp_server'], self.gmail_config['smtp_port'])
            server.starttls()  # Upgrade connection to secure TLS
            server.login(self.gmail_config['email'], self.gmail_config['app_password'])
            server.send_message(msg)
            server.quit()
            
            print("Email with 4 buttons sent!")
            return True
            
        except Exception as e:
            print(f"Send error: {e}")
            return False

    def start_local_server(self):
        """
        Start a local HTTP server to handle button clicks from the email.
        The server listens on localhost:8080 and processes the 4 decision routes.
        
        Returns:
            bool: True if server started successfully, False otherwise
        """
        try:
            class DecisionHandler(BaseHTTPRequestHandler):
                """
                HTTP request handler for processing button clicks from the email.
                Each button in the email links to a different route on this server.
                """
                sender = None  # Reference to the parent EmailSender instance
                
                def do_GET(self):
                    """
                    Handle GET requests from email button clicks.
                    Routes correspond to the 4 decision options in the email.
                    """
                    if self.sender:
                        if self.path == '/accept_whitelist':
                            # Accept vehicle and add to whitelist for future automatic access
                            print("\nBUTTON CLICKED: ACCEPT + WHITELIST")
                            self.sender.decision = 'accept_whitelist'
                            self._send_response("ACCESS GRANTED + WHITELIST", "Gate opened and plate added to whitelist")
                            
                        elif self.path == '/accept_only':
                            # Accept vehicle once without adding to whitelist
                            print("\nBUTTON CLICKED: ACCEPT ONLY")
                            self.sender.decision = 'accept_only'
                            self._send_response("ACCESS GRANTED", "Gate opened (without whitelist)")
                            
                        elif self.path == '/reject_blacklist':
                            # Reject vehicle and add to blacklist for future automatic rejection
                            print("\nBUTTON CLICKED: REJECT + BLACKLIST")
                            self.sender.decision = 'reject_blacklist'
                            self._send_response("ACCESS DENIED + BLACKLIST", "Access denied and plate added to blacklist")
                            
                        elif self.path == '/reject_only':
                            # Reject vehicle once without adding to blacklist
                            print("\nBUTTON CLICKED: REJECT ONLY")
                            self.sender.decision = 'reject_only'
                            self._send_response("ACCESS DENIED", "Access denied (without blacklist)")
                            
                        else:
                            # Show homepage for any other route
                            self._send_homepage()
                    
                def _send_response(self, title, message):
                    """
                    Send a confirmation HTML page after a decision is made.
                    Also starts the program termination process in a separate thread.
                    
                    Args:
                        title (str): The main title for the response page
                        message (str): Detailed message explaining the action taken
                    """
                    html = f"""
                    <html>
                    <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                        <h1 style="color: #333;">{title}</h1>
                        <p style="font-size: 18px; color: #666;">{message}</p>
                        <p style="color: #999; margin-top: 30px;">Email system completed - Main program continues</p>
                    </body>
                    </html>
                    """
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(html.encode('utf-8'))
                    # Start cleanup in separate thread to avoid blocking
                    threading.Thread(target=self.sender.cleanup_system).start()
                
                def _send_homepage(self):
                    """
                    Display the server homepage with current vehicle information.
                    This page is shown when accessing the server root or unknown routes.
                    """
                    plate_number = self.sender.current_plate
                    html = f"""
                    <html>
                    <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                        <h1>SECURITY SYSTEM</h1>
                        <p>Vehicle detected : <strong>{plate_number}</strong></p>
                        <p>Waiting for decision...</p>
                        <p><em>Use buttons in the email for better experience</em></p>
                    </body>
                    </html>
                    """
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(html.encode('utf-8'))
                    
                def log_message(self, format, *args):
                    """Disable default HTTP server logging to keep console output clean."""
                    pass
            
            # Link this handler instance to the parent EmailSender
            DecisionHandler.sender = self
            
            # Create and start HTTP server on localhost port 8080
            self.server = HTTPServer(('localhost', 8080), DecisionHandler)
            print("Local server: http://localhost:8080")
            
            # Start server in a separate daemon thread so it doesn't block the main program
            server_thread = threading.Thread(target=self.server.serve_forever)
            server_thread.daemon = True  # Thread will exit when main program exits
            server_thread.start()
            return True
            
        except Exception as e:
            print(f"Server error: {e}")
            return False

    def cleanup_system(self):
        """
        Clean up the email system after a decision has been made.
        This method is called when any of the 4 decision buttons is clicked.
        """
        # Brief delay to ensure the HTTP response is sent before shutdown
        time.sleep(1)
        
        # Map decision codes to human-readable text
        decision_text = {
            'accept_whitelist': 'ACCEPT + WHITELIST',
            'accept_only': 'ACCEPT ONLY', 
            'reject_blacklist': 'REJECT + BLACKLIST',
            'reject_only': 'REJECT ONLY'
        }
        
        print(f"Email system completed - Decision: {decision_text.get(self.decision, self.decision)}")
        
        # Shutdown the HTTP server if it's running
        if self.server:
            self.server.shutdown()
        
        # Set flag to indicate system should exit (but don't call sys.exit)
        self._should_exit = True

    def wait_for_decision(self, timeout=120):
        """
        Wait for user to click one of the decision buttons in the email.
        
        Args:
            timeout (int): Maximum time to wait in seconds before timing out
            
        Returns:
            str: The decision made, or "timeout" if no decision within timeout period
        """
        print(f"\nWaiting for decision... (max {timeout}s)")
        print("Click a button in the EMAIL among the 4 options")
        
        # Wait for decision with timeout
        start = time.time()
        while time.time() - start < timeout:
            if self.decision:
                return self.decision
            if self._should_exit:
                return self.decision
            time.sleep(0.5)  # Check every 500ms
        
        return "timeout"

    def run_email_system(self, plate_number: str):
        """
        Simplified method to run the complete email system.
        
        Args:
            plate_number (str): The detected license plate number
            
        Returns:
            str: The decision made by the user
        """
        print("SECURITY SYSTEM WITH 4 BUTTONS IN EMAIL")
        print("=" * 60)
        
        # Step 1: Start the local HTTP server to handle button clicks
        print("\n1. STARTING SERVER...")
        if not self.start_local_server():
            print("Cannot start server")
            return "error"
        
        # Step 2: Send email with 4 decision buttons
        print("\n2. SENDING EMAIL WITH 4 BUTTONS...")
        if self.send_vehicle_alert(plate_number):
            print("Email with 4 options sent! Check your mailbox")
            
            # Step 3: Wait for user to click a button in the email
            decision = self.wait_for_decision(timeout=120)
            
            if decision == "timeout":
                print("\nTIMEOUT - No action received")
                # Cleanup server
                if self.server:
                    self.server.shutdown()
                return "timeout"
            else:
                return decision
                
        print("Server stopped")
        return "error"

def main():
    """
    Main function that orchestrates the entire vehicle security alert process.
    Sequence: Start server → Send email → Wait for decision → Process result
    """
    print("SECURITY SYSTEM WITH 4 BUTTONS IN EMAIL")
    print("=" * 60)
    
    # Create the main EmailSender instance
    sender = EmailSender()
    
    # Step 1: Start the local HTTP server to handle button clicks
    print("\n1. STARTING SERVER...")
    if not sender.start_local_server():
        print("Cannot start server")
        return
    
    # Step 2: Send email with 4 decision buttons
    print("\n2. SENDING EMAIL WITH 4 BUTTONS...")
    plate = "AB-123-CD"  # Example license plate - in real system this would come from detection
    if sender.send_vehicle_alert(plate):
        print("Email with 4 options sent! Check your mailbox")
        
        # Step 3: Wait for user to click a button in the email
        decision = sender.wait_for_decision(timeout=120)
        
        if decision == "timeout":
            print("\nTIMEOUT - No action received")
        else:
            # If a decision is made, the program will automatically terminate
            # via the stop_program method called from the HTTP handler
            pass
            
    print("Server stopped")
    # Cleanup: shutdown server if it's still running
    if sender.server:
        sender.server.shutdown()

if __name__ == "__main__":
    """
    Program entry point. This ensures the main function only runs when
    the script is executed directly, not when imported as a module.
    """
    main()