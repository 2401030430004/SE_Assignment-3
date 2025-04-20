import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os
import json

class PersonalFinanceTracker:
    def __init__(self):
        # Create data directory in the script location
        self.app_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(self.app_dir, "finance_data")
        self.images_dir = os.path.join(self.data_dir, "images")
        
        # Ensure directories exist
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.images_dir, exist_ok=True)
        
        # Set data file path
        self.data_file = os.path.join(self.data_dir, 'finance_data.csv')
        
        self.categories = [
            'Food', 'Transportation', 'Housing', 'Entertainment',
            'Utilities', 'Healthcare', 'Shopping', 'Education', 'Other'
        ]
        
        # Create or load the data file
        if os.path.exists(self.data_file):
            self.df = pd.read_csv(self.data_file)
            # Convert date strings to datetime objects
            self.df['Date'] = pd.to_datetime(self.df['Date'])
        else:
            self.df = pd.DataFrame(columns=['Date', 'Amount', 'Category', 'Description'])
            self.df['Date'] = pd.to_datetime(self.df['Date'])
            self.save_data()
    
    def add_expense(self, amount, category, description, date=None):
        """Add a new expense to the tracker"""
        if date is None:
            date = datetime.now()
        else:
            try:
                date = pd.to_datetime(date)
            except:
                print("Invalid date format. Using current date.")
                date = datetime.now()

        if category not in self.categories:
            print(f"Invalid category. Please choose from: {', '.join(self.categories)}")
            return False

        # Create new expense with explicit dtypes
        new_expense = pd.DataFrame({
            'Date': [date],
            'Amount': [float(amount)],
            'Category': [category],
            'Description': [description]
        })

        # Ensure dtypes match before concatenation
        for col in self.df.columns:
            if col in new_expense.columns:
                new_expense[col] = new_expense[col].astype(self.df[col].dtype)

        self.df = pd.concat([self.df, new_expense], ignore_index=True)
        self.save_data()
        print("Expense added successfully!")
        return True
    
    def save_data(self):
        """Save the data to CSV file"""
        self.df.to_csv(self.data_file, index=False)
    
    def get_expenses_by_category(self):
        """Return a summary of expenses by category"""
        return self.df.groupby('Category')['Amount'].sum().sort_values(ascending=False)
    
    def get_expenses_by_month(self):
        """Return a summary of expenses by month"""
        self.df['Month'] = self.df['Date'].dt.strftime('%Y-%m')
        monthly_expenses = self.df.groupby('Month')['Amount'].sum()
        return monthly_expenses
    
    def get_category_expenses_by_month(self):
        """Return expenses by category for each month"""
        self.df['Month'] = self.df['Date'].dt.strftime('%Y-%m')
        return self.df.pivot_table(
            index='Month', 
            columns='Category', 
            values='Amount', 
            aggfunc='sum'
        ).fillna(0)
        
    def visualize_expenses_by_category(self):
        """Create a pie chart of expenses by category"""
        expenses_by_category = self.get_expenses_by_category()
        
        plt.figure(figsize=(10, 6))
        plt.pie(
            expenses_by_category, 
            labels=expenses_by_category.index,
            autopct='%1.1f%%',
            startangle=90,
            shadow=True
        )
        plt.axis('equal')  # Equal aspect ratio ensures the pie chart is circular
        plt.title('Expenses by Category')
        plt.tight_layout()
        
        # Save in images directory
        file_path = os.path.join(self.images_dir, 'expenses_by_category.png')
        plt.savefig(file_path)
        plt.show()
        print(f"Chart saved to: {file_path}")
        
    def visualize_monthly_trend(self):
        """Create a line chart of expenses by month"""
        monthly_expenses = self.get_expenses_by_month()
        
        plt.figure(figsize=(12, 6))
        monthly_expenses.plot(kind='line', marker='o')
        plt.title('Monthly Expense Trend')
        plt.xlabel('Month')
        plt.ylabel('Total Expenses')
        plt.grid(True)
        plt.tight_layout()
        
        # Save in images directory
        file_path = os.path.join(self.images_dir, 'monthly_expenses.png')
        plt.savefig(file_path)
        plt.show()
        print(f"Chart saved to: {file_path}")
    
    def visualize_category_trends(self):
        """Create a stacked bar chart of category expenses by month"""
        category_by_month = self.get_category_expenses_by_month()
        
        plt.figure(figsize=(14, 8))
        category_by_month.plot(kind='bar', stacked=True)
        plt.title('Monthly Expenses by Category')
        plt.xlabel('Month')
        plt.ylabel('Expenses')
        plt.legend(title='Category', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        
        # Save in images directory
        file_path = os.path.join(self.images_dir, 'category_expenses_by_month.png')
        plt.savefig(file_path)
        plt.show()
        print(f"Chart saved to: {file_path}")
    
    def generate_monthly_report(self, month=None):
        """Generate a report for a specific month or the current month"""
        if month is None:
            month = datetime.now().strftime('%Y-%m')
            
        self.df['Month'] = self.df['Date'].dt.strftime('%Y-%m')
        month_data = self.df[self.df['Month'] == month]
        
        if len(month_data) == 0:
            print(f"No expenses found for {month}")
            return
        
        total_spent = month_data['Amount'].sum()
        category_spending = month_data.groupby('Category')['Amount'].sum().sort_values(ascending=False)
        
        print(f"\n===== Monthly Report for {month} =====")
        print(f"Total Spent: ₹{total_spent:.2f}")
        print("\nBreakdown by Category:")
        for category, amount in category_spending.items():
            percentage = (amount / total_spent) * 100
            print(f"{category}: ₹{amount:.2f} ({percentage:.1f}%)")
        
        # Top 5 expenses
        top_expenses = month_data.sort_values('Amount', ascending=False).head(5)
        print("\nTop 5 Expenses:")
        for idx, expense in top_expenses.iterrows():
            print(f"{expense['Date'].strftime('%Y-%m-%d')} - {expense['Category']} - {expense['Description']}: ₹{expense['Amount']:.2f}")
        
        # Generate and save text report
        report_path = os.path.join(self.data_dir, f'report_{month}.txt')
        with open(report_path, 'w', encoding='utf-8') as f:  # Add encoding='utf-8' here
            f.write(f"===== Monthly Report for {month} =====\n")
            f.write(f"Total Spent: ₹{total_spent:.2f}\n\n")
            f.write("Breakdown by Category:\n")
            for category, amount in category_spending.items():
                percentage = (amount / total_spent) * 100
                f.write(f"{category}: ₹{amount:.2f} ({percentage:.1f}%)\n")
            
            f.write("\nTop 5 Expenses:\n")
            for idx, expense in top_expenses.iterrows():
                f.write(f"{expense['Date'].strftime('%Y-%m-%d')} - {expense['Category']} - {expense['Description']}: ₹{expense['Amount']:.2f}\n")
        
        print(f"Report saved to: {report_path}")


def interactive_menu():
    """Display an interactive menu for the finance tracker"""
    tracker = PersonalFinanceTracker()
    
    while True:
        print("\n===== Personal Finance Tracker =====")
        print("1. Add a new expense")
        print("2. View expenses by category")
        print("3. View monthly expense trend")
        print("4. View expenses by category per month")
        print("5. Generate monthly report")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ")
        
        if choice == '1':
            try:
                amount = float(input("Enter amount (₹): "))
            except ValueError:
                print("Invalid amount. Please enter a number.")
                continue
            
            print("\nCategories:")
            for i, category in enumerate(tracker.categories, 1):
                print(f"{i}. {category}")
            
            try:
                cat_choice = int(input("Choose category number: "))
                if 1 <= cat_choice <= len(tracker.categories):
                    category = tracker.categories[cat_choice-1]
                else:
                    print("Invalid category choice")
                    continue
            except ValueError:
                print("Please enter a valid number")
                continue
                    
            description = input("Enter description: ")
            date_str = input("Enter date (YYYY-MM-DD) or leave blank for today: ")
            
            date = None if date_str == "" else date_str
            tracker.add_expense(amount, category, description, date)
            
        elif choice == '2':
            expenses_by_category = tracker.get_expenses_by_category()
            if expenses_by_category.empty:
                print("No expenses recorded yet.")
                continue
                
            print("\n===== Expenses by Category =====")
            for category, amount in expenses_by_category.items():
                print(f"{category}: ₹{amount:.2f}")
            
            # Visualize
            tracker.visualize_expenses_by_category()
            
        elif choice == '3':
            monthly_expenses = tracker.get_expenses_by_month()
            if monthly_expenses.empty:
                print("No expenses recorded yet.")
                continue
                
            print("\n===== Monthly Expenses =====")
            for month, amount in monthly_expenses.items():
                print(f"{month}: ₹{amount:.2f}")
            
            # Visualize
            tracker.visualize_monthly_trend()
            
        elif choice == '4':
            if tracker.df.empty:
                print("No expenses recorded yet.")
                continue
                
            tracker.visualize_category_trends()
            
        elif choice == '5':
            if tracker.df.empty:
                print("No expenses recorded yet.")
                continue
                
            month = input("Enter month (YYYY-MM) or leave blank for current month: ")
            if month:
                # Validate month format
                try:
                    # Try to parse as a date
                    pd.to_datetime(month + "-01")
                except ValueError:
                    print("Invalid month format. Please use YYYY-MM format.")
                    continue
            
            tracker.generate_monthly_report(month if month else None)
            
        elif choice == '6':
            print("Thank you for using the Personal Finance Tracker!")
            break
            
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    interactive_menu()
