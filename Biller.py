# Import the style components from tStyle.py
from tStyle import BankAccount, BillingStyle, AccountManager, generate_token
import sys


class BillingSystem:
    """Main billing system logic class"""

    def __init__(self):
        self.account_manager = AccountManager()
        self.style = BillingStyle()
        self.current_account = None
        self.running = True

    def start(self):
        """Start the billing system"""
        self.style.clear_screen()
        self.style.print_header("JM TSIE BILLING SYSTEM")
        print("Welcome to the billing management system!")
        print("Features: Account Management, Transactions, File Storage")
        self.style.print_separator()

        self.main_loop()

    def main_loop(self):
        """Main program loop"""
        while self.running:
            try:
                if self.current_account:
                    self.show_main_menu()
                else:
                    self.show_account_menu()
            except KeyboardInterrupt:
                self.handle_exit()
            except Exception as e:
                self.style.print_error_message(f"System error: {e}")
                print("Please try again or restart the system.")

    def show_account_menu(self):
        """Display account selection/creation menu"""
        accounts = self.account_manager.get_accounts_list()

        self.style.print_header("ACCOUNT MANAGEMENT")

        if accounts:
            self.style.print_accounts_list(accounts)
            print("Available Options:")
        else:
            print("No accounts found. Create your first account!")

        menu_options = [
            "Create New Account",
            "Select Existing Account",
            "View Account Details",
            "Exit System"
        ]

        self.style.print_menu(menu_options)

        choice = self.get_menu_choice(1, 4)
        if choice:
            self.handle_account_menu_choice(choice)

    def handle_account_menu_choice(self, choice):
        """Handle account menu selections"""
        if choice == 1:
            self.create_new_account()
        elif choice == 2:
            self.select_account()
        elif choice == 3:
            self.view_account_details()
        elif choice == 4:
            self.handle_exit()

    def create_new_account(self):
        """Create a new user account"""
        self.style.print_section_title("CREATE NEW ACCOUNT")

        try:
            # Get account name
            name = input("Enter account holder name: ").strip()
            if not name:
                self.style.print_error_message("Name cannot be empty!")
                return

            # Get initial balance
            balance_input = input("Enter initial balance (press Enter for R1,000,000): ").strip()

            if balance_input:
                try:
                    # Remove currency symbols and commas
                    clean_input = balance_input.replace('R', '').replace(',', '').strip()
                    initial_balance = float(clean_input)

                    if initial_balance < 0:
                        self.style.print_error_message("Balance cannot be negative!")
                        return

                except ValueError:
                    self.style.print_error_message("Invalid balance format!")
                    return
            else:
                initial_balance = 1000000

            # Create the account
            account_id, account_info = self.account_manager.create_new_account(name, initial_balance)

            self.style.print_success_message(
                f"Account created successfully!\n"
                f"Account ID: {account_id}\n"
                f"Name: {name}\n"
                f"Initial Balance: R{initial_balance:,.2f}"
            )

            # Ask if user wants to login immediately
            login_choice = input("Login to this account now? (y/N): ").lower()
            if login_choice in ['y', 'yes']:
                self.current_account = BankAccount(account_id, self.account_manager)
                self.style.print_success_message(f"Logged into account: {name}")

        except Exception as e:
            self.style.print_error_message(f"Failed to create account: {e}")

    def select_account(self):
        """Select an existing account"""
        accounts = self.account_manager.get_accounts_list()

        if not accounts:
            self.style.print_error_message("No accounts available!")
            return

        self.style.print_section_title("SELECT ACCOUNT")
        self.style.print_accounts_list(accounts)

        try:
            account_id = input("Enter Account ID: ").strip()

            if account_id in accounts:
                self.current_account = BankAccount(int(account_id), self.account_manager)
                account_name = accounts[account_id]['name']
                balance = self.current_account.get_balance()

                self.style.print_success_message(
                    f"Successfully logged into: {account_name}\n"
                    f"Current Balance: R{balance:,.2f}"
                )
            else:
                self.style.print_error_message("Account ID not found!")

        except ValueError:
            self.style.print_error_message("Invalid Account ID!")
        except Exception as e:
            self.style.print_error_message(f"Login error: {e}")

    def view_account_details(self):
        """View detailed information for all accounts"""
        accounts = self.account_manager.get_accounts_list()

        self.style.print_section_title("ACCOUNT DETAILS")

        if not accounts:
            print("No accounts found.")
        else:
            for acc_id, acc_info in accounts.items():
                # Get current balance from file
                temp_account = BankAccount(int(acc_id), self.account_manager)
                current_balance = temp_account.get_balance()

                print(f"\nAccount ID: {acc_id}")
                print(f"Name: {acc_info['name']}")
                print(f"Created: {acc_info['created']}")
                print(f"Current Balance: R{current_balance:,.2f}")
                print("-" * 40)

        input("\nPress Enter to continue...")

    def show_main_menu(self):
        """Display main menu for logged-in users"""
        accounts = self.account_manager.get_accounts_list()
        account_name = accounts[str(self.current_account.account_id)]['name']
        current_balance = self.current_account.get_balance()

        self.style.print_header("MAIN MENU")
        print(f"Account: {account_name}")
        print(f"Balance: R{current_balance:,.2f}")

        menu_options = [
            "Purchase Services",
            "Pay Bills",
            "Deposit Money",
            "Withdraw Money",
            "Check Balance",
            "Account Information",
            "Logout",
            "Exit System"
        ]

        self.style.print_menu(menu_options)

        choice = self.get_menu_choice(1, 8)
        if choice:
            self.handle_main_menu_choice(choice)

    def handle_main_menu_choice(self, choice):
        """Handle main menu selections"""
        if choice == 1:
            self.purchase_services_menu()
        elif choice == 2:
            self.pay_bills_menu()
        elif choice == 3:
            self.deposit_money()
        elif choice == 4:
            self.withdraw_money()
        elif choice == 5:
            self.check_balance()
        elif choice == 6:
            self.show_account_info()
        elif choice == 7:
            self.logout()
        elif choice == 8:
            self.handle_exit()

    def purchase_services_menu(self):
        """Handle service purchases"""
        self.style.print_section_title("PURCHASE SERVICES")

        services = [
            ("Electricity", "Electricity Tokens"),
            ("Data", "Mobile Data Bundle"),
            ("Airtime", "Mobile Airtime"),
            ("Water", "Water Tokens"),
            ("Gaming", "Gaming Voucher")
        ]

        print("Available Services:")
        for i, (service, description) in enumerate(services, 1):
            print(f"{i}. {service} - {description}")
        print(f"{len(services) + 1}. Back to Main Menu")

        self.style.print_separator()

        choice = self.get_menu_choice(1, len(services) + 1)
        if choice and choice <= len(services):
            service_name, service_desc = services[choice - 1]
            self.process_purchase(service_name, service_desc)
        # If choice is len(services) + 1, it goes back automatically

    def pay_bills_menu(self):
        """Handle bill payments"""
        self.style.print_section_title("PAY BILLS")

        bills = [
            ("Netflix", "Streaming Subscription"),
            ("Internet", "Internet Service Provider"),
            ("Insurance", "Monthly Insurance Premium"),
            ("Gym", "Gym Membership Fee"),
            ("Rent", "Monthly Rent Payment")
        ]

        print("Available Bills:")
        for i, (bill, description) in enumerate(bills, 1):
            print(f"{i}. {bill} - {description}")
        print(f"{len(bills) + 1}. Back to Main Menu")

        self.style.print_separator()

        choice = self.get_menu_choice(1, len(bills) + 1)
        if choice and choice <= len(bills):
            bill_name, bill_desc = bills[choice - 1]
            self.process_payment(bill_name, bill_desc)

    def process_purchase(self, service, description):
        """Process a service purchase"""
        self.style.print_section_title(f"PURCHASE {service.upper()}")
        print(f"Service: {description}")

        try:
            amount = float(input(f"Enter amount for {service}: R"))

            if amount <= 0:
                self.style.print_error_message("Amount must be greater than zero!")
                return

            success, message = self.current_account.withdraw(amount)

            if success:
                token = generate_token()
                self.style.print_transaction(amount, service, token)
                print(f"New Balance: R{self.current_account.get_balance():,.2f}")
                self.update_account_registry()
            else:
                self.style.print_error_message(f"Purchase failed: {message}")

        except ValueError:
            self.style.print_error_message("Invalid amount! Please enter a valid number.")
        except Exception as e:
            self.style.print_error_message(f"Purchase error: {e}")

    def process_payment(self, bill, description):
        """Process a bill payment"""
        self.style.print_section_title(f"PAY {bill.upper()}")
        print(f"Bill: {description}")

        try:
            amount = float(input(f"Enter payment amount for {bill}: R"))

            if amount <= 0:
                self.style.print_error_message("Amount must be greater than zero!")
                return

            success, message = self.current_account.withdraw(amount)

            if success:
                self.style.print_transaction(amount, f"{bill} Bill Payment")
                print(f"New Balance: R{self.current_account.get_balance():,.2f}")
                self.update_account_registry()
            else:
                self.style.print_error_message(f"Payment failed: {message}")

        except ValueError:
            self.style.print_error_message("Invalid amount! Please enter a valid number.")
        except Exception as e:
            self.style.print_error_message(f"Payment error: {e}")

    def deposit_money(self):
        """Handle money deposits"""
        self.style.print_section_title("DEPOSIT MONEY")

        try:
            amount = float(input("Enter deposit amount: R"))

            if amount <= 0:
                self.style.print_error_message("Amount must be greater than zero!")
                return

            success, message = self.current_account.deposit(amount)

            if success:
                self.style.print_success_message(
                    f"Deposit successful!\n"
                    f"Amount Deposited: R{amount:,.2f}\n"
                    f"New Balance: R{self.current_account.get_balance():,.2f}"
                )
                self.update_account_registry()
            else:
                self.style.print_error_message(f"Deposit failed: {message}")

        except ValueError:
            self.style.print_error_message("Invalid amount! Please enter a valid number.")
        except Exception as e:
            self.style.print_error_message(f"Deposit error: {e}")

    def withdraw_money(self):
        """Handle money withdrawals"""
        self.style.print_section_title("WITHDRAW MONEY")

        try:
            current_balance = self.current_account.get_balance()
            print(f"Available Balance: R{current_balance:,.2f}")

            amount = float(input("Enter withdrawal amount: R"))

            if amount <= 0:
                self.style.print_error_message("Amount must be greater than zero!")
                return

            success, message = self.current_account.withdraw(amount)

            if success:
                self.style.print_success_message(
                    f"Withdrawal successful!\n"
                    f"Amount Withdrawn: R{amount:,.2f}\n"
                    f"New Balance: R{self.current_account.get_balance():,.2f}"
                )
                self.update_account_registry()
            else:
                self.style.print_error_message(f"Withdrawal failed: {message}")

        except ValueError:
            self.style.print_error_message("Invalid amount! Please enter a valid number.")
        except Exception as e:
            self.style.print_error_message(f"Withdrawal error: {e}")

    def check_balance(self):
        """Display current account balance"""
        self.style.print_section_title("ACCOUNT BALANCE")
        balance = self.current_account.get_balance()
        print(f"Your current balance is: R{balance:,.2f}")
        input("\nPress Enter to continue...")

    def show_account_info(self):
        """Display detailed account information"""
        self.style.print_section_title("ACCOUNT INFORMATION")
        info = self.current_account.get_account_info()
        print(info)
        input("\nPress Enter to continue...")

    def update_account_registry(self):
        """Update account balance in the registry"""
        try:
            accounts = self.account_manager.get_accounts_list()
            account_id_str = str(self.current_account.account_id)
            if account_id_str in accounts:
                accounts[account_id_str]['balance'] = self.current_account.get_balance()
                self.account_manager.save_accounts_list(accounts)
        except Exception as e:
            print(f"Warning: Failed to update account registry: {e}")

    def logout(self):
        """Logout current user"""
        if self.current_account:
            self.update_account_registry()
            self.current_account = None
            self.style.print_success_message("Successfully logged out!")

    def get_menu_choice(self, min_choice, max_choice):
        """Get and validate menu choice"""
        try:
            choice = int(input(f"Select option ({min_choice}-{max_choice}): "))
            if min_choice <= choice <= max_choice:
                self.style.print_separator()
                return choice
            else:
                self.style.print_error_message(f"Please select a number between {min_choice} and {max_choice}!")
                return None
        except ValueError:
            self.style.print_error_message("Please enter a valid number!")
            return None
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            return None

    def handle_exit(self):
        """Handle system exit"""
        self.style.print_section_title("EXIT CONFIRMATION")

        if self.current_account:
            self.update_account_registry()

        response = input("Are you sure you want to exit? (y/N): ").lower()

        if response in ['y', 'yes']:
            self.style.print_header("GOODBYE")
            print("Thank you for using JM TSIE Billing System!")
            print("All account data has been saved successfully.")
            print("Have a great day!")
            self.style.print_separator()
            self.running = False
            sys.exit(0)
        else:
            print("Returning to main menu...")


# Main execution
if __name__ == "__main__":
    try:
        system = BillingSystem()
        system.start()
    except KeyboardInterrupt:
        print("\nProgram interrupted. Goodbye!")
    except Exception as e:
        print(f"Fatal system error: {e}")
        print("Please restart the program.")
        sys.exit(1)