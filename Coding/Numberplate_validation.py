class UnknownPlateHandler:
    """
    Implements logic for unknown license plates
    Alarm notification & manual approval/rejection via input()
    """
    
    def handle_unknown_plate(self, plate_number: str) -> bool:
        """
        Processes an unknown license plate according to the criteria:
        IF plate unknown, THEN the owner's decision is requested.
        
        Args:
            plate_number (str): Detected license plate number
            
        Returns:
            bool: True if access granted, False if denied
        """
        
        # Alarm notification - simulating alert sending to owner
        self._send_alarm_notification(plate_number)
        
        # Manual approval/rejection via input()
        decision = self._get_owner_decision(plate_number)
        
        # Process the decision
        return self._process_decision(decision, plate_number)
    
    def _send_alarm_notification(self, plate_number: str):
        """Simulates sending an alert to the owner"""
        print(f"ALARM: Unknown license plate detected: {plate_number}")
        print("Notification sent to owner...")
    
    def _get_owner_decision(self, plate_number: str) -> str:
        """
        Requests owner's decision via input()
        
        Returns:
            str: 'ALLOW' to authorize, 'DENY' to refuse
        """
        print(f"\n Unrecognized vehicle - License plate: {plate_number}")
        print("What would you like to do?")
        print("1.Grant access")
        print("2.Deny access")
        
        while True:
            try:
                choice = input("Your choice (1 or 2): ").strip()
                
                if choice == '1':
                    return 'ALLOW'
                elif choice == '2':
                    return 'DENY'
                else:
                    print("Invalid choice. Please enter 1 to ALLOW or 2 to DENY.")
                    
            except KeyboardInterrupt:
                print("\nInterruption detected. Access denied for security reasons.")
                return 'DENY'
    
    def _process_decision(self, decision: str, plate_number: str) -> bool:
        """
        Processes the owner's decision
        
        Returns:
            bool: True if access granted, False if denied
        """
        if decision == 'ALLOW':
            print(f"Access GRANTED for license plate: {plate_number}")
            print(f"The portal is opening")
            return True
        else:  # DENY or any other value
            print(f"Access DENIED for license plate: {plate_number}")
            print(f"The portal is closed")
            return False


# Test functionality
if __name__ == "__main__":
    print("Testing unknown license plate logic")
    
    handler = UnknownPlateHandler()
    
    # Test avec une plaque fixe
    test_plate = "AB-123-CD"
    result = handler.handle_unknown_plate(test_plate)
    
    print(f"\n Final result: Access {'GRANTED' if result else 'DENIED'}")