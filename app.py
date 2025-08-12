from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import re

# Initialize the Flask app
app = Flask(__name__)
# The database file will be created in the instance folder
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance.db'
app.config['SECRET_KEY'] = 'e9f09e527c3116ce8b2794b67add37781c156f01029dca9c'
db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    # A backref to easily access the transactions for a user
    transactions = db.relationship('Transaction', backref='user', lazy=True)
    budgets = db.relationship('Budget', backref='user', lazy=True)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(10), nullable=False)  # 'income' or 'expense'
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(200), nullable=True)

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    # We will track the budget for a specific month and year
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)

# Routes

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    transactions = Transaction.query.filter_by(user_id=user_id).order_by(Transaction.date.desc()).all()
    
    # Calculate totals
    total_income = sum(t.amount for t in transactions if t.type == 'income')
    total_expense = sum(t.amount for t in transactions if t.type == 'expense')
    net_balance = total_income - total_expense

    # Get the current month and year for budget tracking
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # Calculate spending for the current month by category
    spending_this_month = db.session.query(
        Transaction.category,
        db.func.sum(Transaction.amount)
    ).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'expense',
        db.func.substr(Transaction.date, 6, 2).cast(db.Integer) == current_month,
        db.func.substr(Transaction.date, 1, 4).cast(db.Integer) == current_year
    ).group_by(Transaction.category).all()
    
    # Get budgets for the current month
    budgets = Budget.query.filter_by(user_id=user_id, month=current_month, year=current_year).all()
    
    # Create a dictionary for easy lookup of spending and budget
    spending_dict = {category: amount for category, amount in spending_this_month}
    budgets_with_spending = []
    for budget in budgets:
        budgets_with_spending.append({
            'category': budget.category,
            'budget_amount': budget.amount,
            'spent_amount': spending_dict.get(budget.category, 0.0) # Default to 0 if no spending in that category
        })
    
    return render_template(
        'index.html',
        transactions=transactions,
        total_income=total_income,
        total_expense=total_expense,
        net_balance=net_balance,
        budgets_with_spending=budgets_with_spending
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register'))

        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return redirect(url_for('register'))

        # Check for password strength
        if not re.search(r"[A-Z]", password) or \
           not re.search(r"[0-9]", password) or \
           not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]+", password):
            flash('Password must contain an uppercase letter, a number, and a special character.', 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    if 'user_id' not in session:
        flash('You must be logged in to add a transaction.', 'danger')
        return redirect(url_for('login'))
        
    try:
        amount = float(request.form['amount'])
        type = request.form['type']
        category = request.form['category']
        date = request.form['date']
        description = request.form.get('description', '')

        new_transaction = Transaction(
            user_id=session['user_id'],
            amount=amount,
            type=type,
            category=category,
            date=date,
            description=description
        )
        db.session.add(new_transaction)
        db.session.commit()
        flash('Transaction added successfully!', 'success')
    except (ValueError, KeyError) as e:
        flash(f'An error occurred: {e}. Please ensure all fields are correct.', 'danger')

    return redirect(url_for('index'))
    
@app.route('/edit_transaction/<int:transaction_id>', methods=['POST'])
def edit_transaction(transaction_id):
    if 'user_id' not in session:
        flash('You must be logged in to edit a transaction.', 'danger')
        return redirect(url_for('login'))
        
    transaction = Transaction.query.get(transaction_id)
    if not transaction or transaction.user_id != session['user_id']:
        flash('Transaction not found or you do not have permission to edit it.', 'danger')
        return redirect(url_for('index'))
        
    try:
        transaction.amount = float(request.form['amount'])
        transaction.type = request.form['type']
        transaction.category = request.form['category']
        transaction.date = request.form['date']
        transaction.description = request.form.get('description', '')
        
        db.session.commit()
        flash('Transaction updated successfully!', 'success')
    except (ValueError, KeyError) as e:
        flash(f'An error occurred: {e}. Please ensure all fields are correct.', 'danger')
        
    return redirect(url_for('index'))

@app.route('/delete_transaction/<int:transaction_id>', methods=['POST'])
def delete_transaction(transaction_id):
    if 'user_id' not in session:
        flash('You must be logged in to delete a transaction.', 'danger')
        return redirect(url_for('login'))
        
    transaction = Transaction.query.get(transaction_id)
    if not transaction or transaction.user_id != session['user_id']:
        flash('Transaction not found or you do not have permission to delete it.', 'danger')
        return redirect(url_for('index'))

    db.session.delete(transaction)
    db.session.commit()
    flash('Transaction deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/add_budget', methods=['POST'])
def add_budget():
    if 'user_id' not in session:
        flash('You must be logged in to add a budget.', 'danger')
        return redirect(url_for('login'))
    
    try:
        category = request.form['category']
        amount = float(request.form['amount'])
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        # Check if a budget already exists for this category in the current month
        existing_budget = Budget.query.filter_by(
            user_id=session['user_id'],
            category=category,
            month=current_month,
            year=current_year
        ).first()

        if existing_budget:
            # Update existing budget
            existing_budget.amount = amount
            flash(f'Budget for {category} updated successfully!', 'success')
        else:
            # Add new budget
            new_budget = Budget(
                user_id=session['user_id'],
                category=category,
                amount=amount,
                month=current_month,
                year=current_year
            )
            db.session.add(new_budget)
            flash('Budget added successfully!', 'success')
            
        db.session.commit()
        
    except (ValueError, KeyError) as e:
        flash(f'An error occurred: {e}. Please ensure all fields are correct.', 'danger')

    return redirect(url_for('index'))

# Create database tables if they don't exist
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
