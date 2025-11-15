# Password Manager

A secure command-line password manager that stores and encrypts passwords locally using SQLite and Fernet encryption.

## Features

- **Secure Encryption**: Uses Fernet symmetric encryption (AES 128 in CBC mode) to encrypt passwords
- **Password Validation**: Enforces strong password requirements:
  - Minimum 8 characters
  - At least one uppercase letter
  - At least one lowercase letter
  - At least one number
  - At least one special character
- **Local Storage**: Passwords stored in a local SQLite database
- **Duplicate Prevention**: Prevents storing multiple passwords for the same service
- **CLI Interface**: Simple command-line interface for easy interaction

## Requirements

- Python 3.6+
- cryptography library

## Installation

1. Clone the repository:
```bash
git clone https://github.com/aydinefendi/pcs-pm.git
cd pcs-pm
```

2. Install dependencies:
```bash
pip install cryptography
```

## Usage

Run the password manager:
```bash
python password_mngr.py
```

### Menu Options

1. **Add Password**: Store a new password for a service
   - Enter service name (e.g., `gmail.com`)
   - Enter and confirm password (must meet validation requirements)
   - Maximum 3 attempts for both password entry and confirmation

2. **Get Password**: Retrieve a stored password
   - Enter service name
   - Password will be displayed in plain text

3. **Exit**: Close the application

### Example Session

```
=== Password Manager ===
1. Add password
2. Get password
3. Exit

Enter choice (1-3): 1
Password should be at least 8 characters long and include at least one uppercase letter, one lowercase letter, one number, and one special character
Enter service name (e.g., gmail.com): gmail.com
Enter password: 
Confirm password: 
Password for gmail.com saved successfully

=== Password Manager ===
1. Add password
2. Get password
3. Exit

Enter choice (1-3): 2
Enter service name (e.g., gmail.com): gmail.com

Service: gmail.com
Password: MySecurePass123!
```

## Security Features

- **Encryption Key**: Auto-generated on first run and stored in `encryption.key`
- **Fernet Encryption**: Provides authenticated encryption with timestamp validation
- **No Plaintext Storage**: Passwords are encrypted before being stored in the database
- **Password Masking**: Uses `getpass` to hide password input in the terminal

## File Structure

```
.
├── password_mngr.py      # Main application code
├── tests.py              # Unit tests
├── passwords.db          # SQLite database (created on first run)
├── encryption.key        # Encryption key (created on first run)
└── README.md             # This file
```

## Testing

The project includes comprehensive unit tests covering:
- Password validation
- Encryption/decryption
- Database operations
- Key file management
- Service duplicate prevention
- Multiple service handling

Run tests with:
```bash
python -m unittest tests.py
```

Or for verbose output:
```bash
python -m unittest tests.py -v
```

### Test Coverage

- ✓ Password validation (length, uppercase, lowercase, numbers, special characters)
- ✓ Encryption produces different ciphertexts for same password
- ✓ Decryption correctly retrieves original password
- ✓ Key file generation and persistence
- ✓ Database creation and table structure
- ✓ Store and retrieve operations
- ✓ Duplicate service prevention
- ✓ Handling non-existent passwords
- ✓ Multiple service management

## Important Notes

⚠️ **Security Warnings:**
- Keep `encryption.key` secure and backed up. If lost, passwords cannot be recovered.
- Do not commit `encryption.key` or `passwords.db` to version control
- This is a learning project. For production use, consider established password managers
- Passwords are displayed in plaintext when retrieved

## Database Schema

```sql
CREATE TABLE passwords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);
```

## Future Enhancements

Potential improvements for future versions:
- Master password authentication
- Update/delete password functionality
- Password strength meter
- Export/import functionality
- Search and list all services
- Clipboard integration (auto-clear after timeout)
- Cross-platform support testing

## License

This project is for educational purposes.

## Author

Aydin Efendi
