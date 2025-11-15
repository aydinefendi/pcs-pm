import sqlite3
import getpass
import os
import re
from cryptography.fernet import Fernet

class PasswordManager:
    def __init__(self, db_name="passwords.db", key_file="encryption.key"):
        """Initialize the password manager with database and encryption"""
        self.db_name = db_name
        self.key_file = key_file
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.fernet = self._initialize_encryption()
        self.create_table()
    
    def create_table(self):
        """Create the passwords table if it doesn't exist"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS passwords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')
        self.conn.commit()

    def _initialize_encryption(self):
        """Load or generate encryption key"""
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
        return Fernet(key)
    
    def encrypt_password(self, password):
        """Encrypt a password using Fernet"""
        return self.fernet.encrypt(password.encode()).decode()
    
    def decrypt_password(self, encrypted_password):
        """Decrypt an encrypted password"""
        return self.fernet.decrypt(encrypted_password.encode()).decode()
    
    def validate_password(self, password):
        """Check if password meets security requirements"""
        errors = []
        
        if len(password) < 8:
            errors.append("- At least 8 characters long")
        
        if not re.search(r'[A-Z]', password):
            errors.append("- At least one uppercase letter")
        
        if not re.search(r'[a-z]', password):
            errors.append("- At least one lowercase letter")
        
        if not re.search(r'\d', password):
            errors.append("- At least one number")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("- At least one special character ")
        
        return len(errors) == 0, errors
    
    def add_password(self, service_name):
        """Add a new password for a service with validation and confirmation"""
        max_attempts = 3
        
        for attempt in range(1, max_attempts + 1):
            password = getpass.getpass("Enter password: ")
           
            is_valid, errors = self.validate_password(password)
            if not is_valid:
                print("\nPassword does not meet requirements:")
                for error in errors:
                    print(error)
                
                if attempt < max_attempts:
                    print(f"\nAttempt {attempt}/{max_attempts}. Please try again.")
                else:
                    print(f"\nFailed after {max_attempts} attempts. Password not saved.")
                    return
                continue
            
            max_attempts_confirm = 3
            
            for attempt_confirm in range(1, max_attempts_confirm + 1):
                confirm = getpass.getpass("Confirm password: ")
                if password == confirm:
                    break
                else:
                    print("Passwords don't match. Please try again.")
                    if attempt_confirm < max_attempts_confirm:
                        print(f"\nAttempt {attempt_confirm}/{max_attempts_confirm}. Please try again.")
                    else:
                        print(f"\nFailed after {max_attempts_confirm} attempts. Password not saved.")
                        return
                    continue
           
            try:
                encrypted = self.encrypt_password(password)
                self.cursor.execute("INSERT INTO passwords (service, password) VALUES (?, ?)", (service_name, encrypted))
                self.conn.commit()
                print(f"Password for {service_name} saved successfully")
                return
            except sqlite3.IntegrityError:
                print(f"Password for {service_name} already exists. Use update instead.")
                return
            except Exception as e:
                print(f"Error saving password: {e}")
                return
    
    def get_password(self, service_name):
        """Retrieve and decrypt a password for a service"""
        try:
            self.cursor.execute("SELECT service, password FROM passwords WHERE service = ?", (service_name,))
            result = self.cursor.fetchone()
            
            if result:
                _, encrypted_password = result
                decrypted = self.decrypt_password(encrypted_password)
                print(f"\nService: {service_name}")
                print(f"Password: {decrypted}")
                return decrypted
            else:
                print(f"No password found for {service_name}")
                return None
        except Exception as e:
            print(f"Error retrieving password: {e}")
            return None
    
    def close(self):
        """Close the database connection"""
        self.conn.close()

def main():
    """Run the password manager CLI."""
    pm = PasswordManager()
    
    while True:
        print("\n=== Password Manager ===")
        print("1. Add password")
        print("2. Get password")
        print("3. Exit")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == '1':
            print("Password should be at least 8 characters long and include at least one uppercase letter, one lowercase letter, one number, and one special character")
            service_name = input("Enter service name (e.g., gmail.com): ")
            pm.add_password(service_name)
        elif choice == '2':
            service_name = input("Enter service name (e.g., gmail.com): ")
            pm.get_password(service_name)
        elif choice == '3':
            print("Goodbye!")
            pm.close()
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
