import unittest
import os
import tempfile
from password_mngr import PasswordManager


class TestPasswordManager(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_db = os.path.join(self.temp_dir, "test_passwords.db")
        self.test_key = os.path.join(self.temp_dir, "test_encryption.key")
        self.pm = PasswordManager(db_name=self.test_db, key_file=self.test_key)
   
    def tearDown(self):
        self.pm.close()
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        if os.path.exists(self.test_key):
            os.remove(self.test_key)
        os.rmdir(self.temp_dir)
  
    def test_password_validation_valid(self):
        valid_password = "MyPass123!"
        is_valid, errors = self.pm.validate_password(valid_password)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_password_validation_too_short(self):
        short_password = "Ab1!"
        is_valid, errors = self.pm.validate_password(short_password)
        self.assertFalse(is_valid)
        self.assertIn("- At least 8 characters long", errors)
    
    def test_password_validation_no_uppercase(self):
        no_upper = "mypass123!"
        is_valid, errors = self.pm.validate_password(no_upper)
        self.assertFalse(is_valid)
        self.assertIn("- At least one uppercase letter", errors)
    
    def test_password_validation_no_lowercase(self):
        no_lower = "MYPASS123!"
        is_valid, errors = self.pm.validate_password(no_lower)
        self.assertFalse(is_valid)
        self.assertIn("- At least one lowercase letter", errors)
    
    def test_password_validation_no_number(self):
        no_number = "MyPassword!"
        is_valid, errors = self.pm.validate_password(no_number)
        self.assertFalse(is_valid)
        self.assertIn("- At least one number", errors)
    
    def test_password_validation_no_special(self):
        no_special = "MyPassword123"
        is_valid, errors = self.pm.validate_password(no_special)
        self.assertFalse(is_valid)
        self.assertIn("- At least one special character ", errors)
    
    def test_encryption_decryption(self):
        original_password = "TestPassword123!"
        encrypted = self.pm.encrypt_password(original_password)
        
        self.assertNotEqual(original_password, encrypted)
        
        decrypted = self.pm.decrypt_password(encrypted)
        self.assertEqual(original_password, decrypted)
    
    def test_encryption_produces_different_ciphertexts(self):
        password = "TestPassword123!"
        encrypted1 = self.pm.encrypt_password(password)
        encrypted2 = self.pm.encrypt_password(password)
        
        self.assertNotEqual(encrypted1, encrypted2)
        
        self.assertEqual(self.pm.decrypt_password(encrypted1), password)
        self.assertEqual(self.pm.decrypt_password(encrypted2), password)
    
    def test_key_file_generation(self):
        self.assertTrue(os.path.exists(self.test_key))
        
        with open(self.test_key, 'rb') as f:
            key = f.read()
        self.assertGreater(len(key), 0)
    
    def test_key_file_persistence(self):
        password = "TestPassword123!"
        encrypted = self.pm.encrypt_password(password)
        self.pm.close()
        
        pm2 = PasswordManager(db_name=self.test_db, key_file=self.test_key)
        decrypted = pm2.decrypt_password(encrypted)
        
        self.assertEqual(password, decrypted)
        pm2.close()
    
    def test_database_creation(self):
        self.assertTrue(os.path.exists(self.test_db))
        
        self.pm.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='passwords'")
        result = self.pm.cursor.fetchone()
        self.assertIsNotNone(result)
    
    def test_get_nonexistent_password(self):
        result = self.pm.get_password("nonexistent_service")
        self.assertIsNone(result)
    
    def test_store_and_retrieve_password(self):
        service = "gmail.com"
        password = "MyGmail123!"
        
        encrypted = self.pm.encrypt_password(password)
        self.pm.cursor.execute("INSERT INTO passwords (service, password) VALUES (?, ?)",(service, encrypted))
        self.pm.conn.commit()
        
        retrieved = self.pm.get_password(service)
        self.assertEqual(password, retrieved)
    
    def test_duplicate_service_prevention(self):
        service = "facebook.com"
        password1 = "MyPass123!"
        password2 = "DifferentPass456!"
        
        encrypted1 = self.pm.encrypt_password(password1)
        self.pm.cursor.execute("INSERT INTO passwords (service, password) VALUES (?, ?)",(service, encrypted1))
        self.pm.conn.commit()
        
        encrypted2 = self.pm.encrypt_password(password2)
        with self.assertRaises(Exception):
            self.pm.cursor.execute("INSERT INTO passwords (service, password) VALUES (?, ?)", (service, encrypted2))
            self.pm.conn.commit()
  
    def test_multiple_services(self):
        services = {
            "gmail.com": "Gmail123!Pass",
            "facebook.com": "Facebook456!Pass",
            "twitter.com": "Twitter789!Pass"
        }
        
        for service, password in services.items():
            encrypted = self.pm.encrypt_password(password)
            self.pm.cursor.execute("INSERT INTO passwords (service, password) VALUES (?, ?)", (service, encrypted))
        self.pm.conn.commit()
        
        for service, expected_password in services.items():
            retrieved = self.pm.get_password(service)
            self.assertEqual(expected_password, retrieved)


if __name__ == '__main__':
    unittest.main()