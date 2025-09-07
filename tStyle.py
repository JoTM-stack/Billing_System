# tstyle.py - Style and utility classes for the billing system
# Handles file operations, account management, and display formatting

import os
import json
from datetime import datetime
import random


class FileManager:
    """Handles all file I/O operations for the billing system"""

    def __init__(self, accounts_folder="accounts", registry_file="accounts_registry.json"):
        self.accounts_folder = accounts_folder
        self.registry_file = registry_file
        self.ensure_directories_exist()

    def ensure_directories_exist(self):
        """Create necessary directories if they don't exist"""
        try:
            if not os.path.exists(self.accounts_folder):
                os.makedirs(self.accounts_folder)
                print(f"Created accounts directory: {self.accounts_folder}")
        except Exception as e:
            print(f"Error creating directories: {e}")

    def load_json_file(self, file_path):
        """Load data from a JSON file"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read().strip()
                    if content:
                        return json.loads(content)
            return {}
        except json.JSONDecodeError as e:
            print(f"Error: Corrupted JSON file {file_path}: {e}")
            # Create backup of corrupted file
            backup_path = f"{file_path}.corrupted_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            try:
                os.rename(file_path, backup_path)
                print(f"Corrupted file backed up to: {backup_path}")
            except Exception:
                pass
            return {}
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return {}

    def save_json_file(self, file_path, data):
        """Save data to a JSON file"""
        try:
            # Create backup before saving
            if os.path.exists(file_path):
                backup_path = f"{file_path}.backup"
                try:
                    with open(file_path, 'r') as src, open(backup_path, 'w') as dst:
                        dst.write(src.read())
                except Exception:
                    pass  # Backup failed, but continue with save

            # Save the data
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving {file_path}: {e}")
            return False

    def get_account_balance_path(self, account_id):
        """Get file path for account balance"""
        return os.path.join(self.accounts_folder, f"account_{account_id}_balance.txt")

    def load_balance_from_file(self, account_id, default_balance=1000000):
        """Load account balance from file"""
        try:
            balance_file = self.get_account_balance_path(account_id)
            if os.path.exists(balance_file):
                with open(balance_file, 'r', encoding='utf-8') as file:
                    content = file.read().strip()
                    if content:
                        balance = float(content)
                        return balance if balance >= 0 else default_balance
            # File doesn't exist, create it with default balance
            self.save_balance_to_file(account_id, default_balance)
            return default_balance
        except (ValueError, FileNotFoundError) as e:
            print(f"Error loading balance for account {account_id}: {e}")
            return default_balance
        except Exception as e:
            print(f"Unexpected error loading balance: {e}")
            return default_balance

    def save_balance_to_file(self, account_id, balance):
        """Save account balance to file"""
        try:
            if balance < 0:
                print(f"Warning: Attempted to save negative balance ({balance}) for account {account_id}")
                return False

            balance_file = self.get_account_balance_path(account_id)

            # Create backup of current balance
            if os.path.exists(balance_file):
                backup_file = f"{balance_file}.backup"
                try:
                    with open(balance_file, 'r') as src, open(backup_file, 'w') as dst:
                        dst.write(src.read())
                except Exception:
                    pass

            # Save new balance
            with open(balance_file, 'w', encoding='utf-8') as file:
                file.write(str(float(balance)))
            return True
        except Exception as e:
            print(f"Error saving balance for account {account_id}: {e}")
            return False


class AccountManager:
    """Manages user accounts and account registry"""

    def __init__(self):
        self.file_manager = FileManager()

    def get_accounts_list(self):
        """Get list of all registered accounts"""
        return self.file_manager.load_json_file(self.file_manager.registry_file)

    def save_accounts_list(self, accounts):
        """Save accounts list to registry"""
        return self.file_manager.save_json_file(self.file_manager.registry_file, accounts)

    def create_new_account(self, account_name, initial_balance=1000000):
        """Create a new account without authentication"""
        try:
            # Validate inputs
            if not account_name or not account_name.strip():
                raise ValueError("Account name cannot be empty")

            initial_balance = float(initial_balance)
            if initial_balance < 0:
                raise ValueError("Initial balance cannot be negative")

            # Load existing accounts
            accounts = self.get_accounts_list()

            # Generate unique account ID
            account_id = 1
            while str(account_id) in accounts:
                account_id += 1

            # Create account information
            account_info = {
                'id': account_id,
                'name': account_name.strip(),
                'created': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'balance': initial_balance
            }

            # Save to registry
            accounts[str(account_id)] = account_info
            if not self.save_accounts_list(accounts):
                raise Exception("Failed to save account registry")

            # Create balance file
            if not self.file_manager.save_balance_to_file(account_id, initial_balance):
                # Rollback registry changes
                del accounts[str(account_id)]
                self.save_accounts_list(accounts)
                raise Exception("Failed to create balance file")

            print(f"Account created successfully: ID {account_id}, Name: {account_name}")
            return account_id, account_info

        except ValueError as e:
            print(f"Invalid input: {e}")
            raise
        except Exception as e:
            print(f"Error creating account: {e}")
            raise


class BankAccount:
    """Represents a user's bank account with file persistence"""

    def __init__(self, account_id, account_manager=None):
        self.account_id = account_id
        self.account_manager = account_manager or AccountManager()
        self.file_manager = self.account_manager.file_manager

        # Load initial balance from file
        self.balance = self.file_manager.load_balance_from_file(account_id)

    def get_balance(self):
        """Get current account balance"""
        return float(self.balance)

    def update_balance_from_file(self):
        """Reload balance from file"""
        self.balance = self.file_manager.load_balance_from_file(self.account_id, self.balance)
        return self.balance

    def save_balance(self):
        """Save current balance to file"""
        return self.file_manager.save_balance_to_file(self.account_id, self.balance)

    def deposit(self, amount):
        """Deposit money into the account"""
        try:
            amount = float(amount)
            if amount <= 0:
                return False, "Deposit amount must be positive"

            # Update balance
            old_balance = self.balance
            self.balance += amount

            # Save to file
            if self.save_balance():
                return True, f"Deposit successful. New balance: R{self.balance:,.2f}"
            else:
                # Rollback on save failure
                self.balance = old_balance
                return False, "Failed to save transaction to file"

        except (ValueError, TypeError):
            return False, "Invalid amount format"
        except Exception as e:
            return False, f"Deposit error: {e}"

    def withdraw(self, amount):
        """Withdraw money from the account"""
        try:
            amount = float(amount)
            if amount <= 0:
                return False, "Withdrawal amount must be positive"

            if amount > self.balance:
                return False, f"Insufficient funds. Available: R{self.balance:,.2f}"

            # Update balance
            old_balance = self.balance
            self.balance -= amount

            # Save to file
            if self.save_balance():
                return True, f"Withdrawal successful. New balance: R{self.balance:,.2f}"
            else:
                # Rollback on save failure
                self.balance = old_balance
                return False, "Failed to save transaction to file"

        except (ValueError, TypeError):
            return False, "Invalid amount format"
        except Exception as e:
            return False, f"Withdrawal error: {e}"

    def get_account_info(self):
        """Get detailed account information"""
        try:
            accounts = self.account_manager.get_accounts_list()
            if str(self.account_id) in accounts:
                account_data = accounts[str(self.account_id)]
                return (
                    f"Account ID: {self.account_id}\n"
                    f"Account Name: {account_data.get('name', 'Unknown')}\n"
                    f"Created: {account_data.get('created', 'Unknown')}\n"
                    f"Current Balance: R{self.balance:,.2f}\n"
                    f"Balance File: {self.file_manager.get_account_balance_path(self.account_id)}"
                )
            else:
                return f"Account ID: {self.account_id}\nBalance: R{self.balance:,.2f}\nStatus: Registry data missing"
        except Exception as e:
            return f"Account ID: {self.account_id}\nBalance: R{self.balance:,.2f}\nError: {e}"


class BillingStyle:
    """Handles all display formatting and user interface styling"""

    def __init__(self, width=70):
        self.width = width
        self.separator = "=" * width
        self.thin_separator = "-" * width

    def print_separator(self):
        """Print main separator line"""
        print(self.separator)

    def print_thin_separator(self):
        """Print thin separator line"""
        print(self.thin_separator)

    def print_header(self, title):
        """Print a formatted header"""
        self.print_separator()
        print(title.center(self.width))
        self.print_separator()

    def print_section_title(self, title):
        """Print a section title"""
        print(f"\n{title}")
        self.print_thin_separator()

    def print_menu(self, options):
        """Print a formatted menu"""
        try:
            for i, option in enumerate(options, 1):
                print(f"{i}. {option}")
            self.print_separator()
        except Exception as e:
            print(f"Menu display error: {e}")
            self.print_separator()

    def print_success_message(self, message):
        """Print a success message"""
        print(f"\n[SUCCESS] {message}")
        self.print_separator()

    def print_error_message(self, message):
        """Print an error message"""
        print(f"\n[ERROR] {message}")
        self.print_separator()

    def print_info_message(self, message):
        """Print an information message"""
        print(f"\n[INFO] {message}")
        self.print_separator()

    def print_warning_message(self, message):
        """Print a warning message"""
        print(f"\n[WARNING] {message}")
        self.print_separator()

    def print_balance(self, balance):
        """Print formatted balance information"""
        try:
            balance = float(balance)
            print(f"\nCurrent Balance: R{balance:,.2f}")
            self.print_separator()
        except Exception as e:
            print(f"\nBalance Display Error: {e}")
            self.print_separator()

    def print_transaction(self, amount, service, token=None):
        """Print transaction confirmation"""
        try:
            amount = float(amount)
            print(f"\n{'TRANSACTION COMPLETED':^{self.width}}")
            self.print_thin_separator()
            print(f"Service: {service}")
            print(f"Amount: R{amount:,.2f}")
            if token:
                print(f"Reference Token: {token}")
            print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            self.print_separator()
        except Exception as e:
            print(f"\nTransaction Display Error: {e}")
            self.print_separator()

    def print_accounts_list(self, accounts):
        """Print formatted list of accounts"""
        try:
            if not accounts:
                print("No accounts registered.")
                return

            print(f"\n{'REGISTERED ACCOUNTS':^{self.width}}")
            self.print_thin_separator()
            print(f"{'ID':<5} {'Name':<25} {'Created':<12} {'Balance'}")
            self.print_thin_separator()

            for acc_id, acc_info in accounts.items():
                if isinstance(acc_info, dict):
                    name = acc_info.get('name', 'Unknown')[:24]  # Truncate if too long
                    created = acc_info.get('created', 'Unknown')[:11]  # Date only
                    balance = acc_info.get('balance', 0)
                    try:
                        balance = float(balance)
                        balance_str = f"R{balance:,.2f}"
                    except (ValueError, TypeError):
                        balance_str = "Error"

                    print(f"{acc_id:<5} {name:<25} {created:<12} {balance_str}")

            self.print_separator()
        except Exception as e:
            print(f"Account list display error: {e}")
            self.print_separator()

    def print_table_header(self, headers):
        """Print formatted table header"""
        header_line = " | ".join(f"{header:^12}" for header in headers)
        print(header_line)
        self.print_thin_separator()

    def print_table_row(self, data):
        """Print formatted table row"""
        row_line = " | ".join(f"{str(item):^12}" for item in data)
        print(row_line)

    def clear_screen(self):
        """Clear the console screen"""
        try:
            # Windows
            if os.name == 'nt':
                os.system('cls')
            # Unix/Linux/MacOS
            else:
                os.system('clear')
        except Exception:
            # Fallback: print multiple newlines
            print('\n' * 50)

    def get_formatted_input(self, prompt, input_type="string"):
        """Get formatted user input with validation"""
        try:
            if input_type == "float":
                while True:
                    try:
                        value = float(input(f"{prompt}: "))
                        return value
                    except ValueError:
                        print("Please enter a valid number.")
            elif input_type == "int":
                while True:
                    try:
                        value = int(input(f"{prompt}: "))
                        return value
                    except ValueError:
                        print("Please enter a valid integer.")
            else:
                return input(f"{prompt}: ").strip()
        except KeyboardInterrupt:
            return None
        except Exception as e:
            print(f"Input error: {e}")
            return None

    def display_loading(self, message="Processing"):
        """Display a simple loading message"""
        print(f"{message}...", end="", flush=True)

    def display_complete(self):
        """Display completion message"""
        print(" Done!")


class TransactionLogger:
    """Handles logging of transactions for audit purposes"""

    def __init__(self, log_folder="logs"):
        self.log_folder = log_folder
        self.ensure_log_folder()

    def ensure_log_folder(self):
        """Create log folder if it doesn't exist"""
        try:
            if not os.path.exists(self.log_folder):
                os.makedirs(self.log_folder)
        except Exception as e:
            print(f"Warning: Could not create log folder: {e}")

    def log_transaction(self, account_id, transaction_type, amount, service=None, token=None):
        """Log a transaction to file"""
        try:
            log_file = os.path.join(self.log_folder, f"account_{account_id}_transactions.log")

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = {
                "timestamp": timestamp,
                "type": transaction_type,
                "amount": float(amount),
                "service": service,
                "token": token
            }

            with open(log_file, 'a', encoding='utf-8') as file:
                file.write(f"{json.dumps(log_entry)}\n")

            return True
        except Exception as e:
            print(f"Warning: Could not log transaction: {e}")
            return False

    def get_transaction_history(self, account_id, limit=10):
        """Get recent transaction history"""
        try:
            log_file = os.path.join(self.log_folder, f"account_{account_id}_transactions.log")

            if not os.path.exists(log_file):
                return []

            transactions = []
            with open(log_file, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            # Get last 'limit' transactions
            for line in lines[-limit:]:
                try:
                    transaction = json.loads(line.strip())
                    transactions.append(transaction)
                except json.JSONDecodeError:
                    continue

            return transactions
        except Exception as e:
            print(f"Error reading transaction history: {e}")
            return []


def generate_token():
    """Generate a random token for purchases"""
    try:
        # Generate 4 groups of 4-digit numbers
        token_parts = [f"{random.randint(1000, 9999)}" for _ in range(4)]
        return " ".join(token_parts)
    except Exception:
        # Fallback token generation using timestamp
        timestamp = str(int(datetime.now().timestamp()))[-8:]
        return f"{timestamp[:4]} {timestamp[4:]}"


def format_currency(amount):
    """Format amount as currency"""
    try:
        return f"R{float(amount):,.2f}"
    except (ValueError, TypeError):
        return f"R{amount}"


def validate_account_name(name):
    """Validate account name format"""
    if not name or not name.strip():
        return False, "Account name cannot be empty"

    name = name.strip()
    if len(name) < 2:
        return False, "Account name must be at least 2 characters"

    if len(name) > 50:
        return False, "Account name cannot exceed 50 characters"

    # Check for invalid characters
    invalid_chars = ['<', '>', '/', '\\', '|', ':', '*', '?', '"']
    if any(char in name for char in invalid_chars):
        return False, "Account name contains invalid characters"

    return True, "Valid account name"


def validate_amount(amount_str):
    """Validate monetary amount"""
    try:
        # Remove currency symbols and spaces
        clean_amount = amount_str.replace('R', '').replace(',', '').replace(' ', '')
        amount = float(clean_amount)

        if amount < 0:
            return False, "Amount cannot be negative"

        if amount > 999999999:  # 999 million limit
            return False, "Amount exceeds maximum limit"
 
        # Check for reasonable decimal places (max 2)
        if '.' in clean_amount and len(clean_amount.split('.')[1]) > 2:
            return False, "Amount cannot have more than 2 decimal places"

        return True, amount
    except ValueError:
        return False, "Invalid amount format"


# Export all classes and functions
__all__ = [
    'FileManager', 'AccountManager', 'BankAccount', 'BillingStyle',
    'TransactionLogger', 'generate_token', 'format_currency',
    'validate_account_name', 'validate_amount'
]