from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import re

# Initialize the Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance.db'
app.config['SECRET_KEY'] = 'e9f09e527c3116ce8b2794b67add37781c156f01029dca9c'
db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(10), nullable=False)  # 'income' or 'expense'
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(200))

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False, unique=False)
    limit = db.Column(db.Float, nullable=False)
    # Ensure a user can only have one budget per category
    __table_args__ = (db.UniqueConstraint('user_id', 'category', name='_user_category_uc'),)

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        user_id = session['user_id']
        # Fetch transactions for the logged-in user, ordered by date
        transactions = Transaction.query.filter_by(user_id=user_id).order_by(Transaction.date.desc()).all()
        
        # Fetch budgets for the logged-in user
        budgets = Budget.query.filter_by(user_id=user_id).all()
        budget_data = {budget.category: budget.limit for budget in budgets}

        # Calculate total income and expenses
        total_income = sum(t.amount for t in transactions if t.type == 'income')
        total_expenses = sum(t.amount for t in transactions if t.type == 'expense')
        
        # Group data for charts
        expense_data = {}
        income_data = {}
        for t in transactions:
            if t.type == 'expense':
                expense_data[t.category] = expense_data.get(t.category, 0) + t.amount
            elif t.type == 'income':
                income_data[t.category] = income_data.get(t.category, 0) + t.amount
        
        return render_template('index.html', 
                               transactions=transactions,
                               total_income=total_income,
                               total_expenses=total_expenses,
                               expense_data=list(expense_data.items()),
                               income_data=list(income_data.items()),
                               budget_data=budget_data)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Check if the username already exists
        user = User.query.filter_by(username=username).first()
        if user:
            flash('That username is already taken. Please choose another.', 'danger')
            return redirect(url_for('register'))
        
        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('register'))
            
        # Validate password strength
        if len(password) < 8 or not re.search(r'[A-Z]', password) or not re.search(r'[0-9]', password) or not re.search(r'[!@#$%^&*()_+\-=\[\]{};\'":\\|,.<>\/?]+', password):
            flash('Password is not strong enough. Please ensure it has at least 8 characters, an uppercase letter, a number, and a special character.', 'danger')
            return redirect(url_for('register'))

        # Hash the password and create a new user
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

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
        else:
            flash('Invalid username or password.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    if 'user_id' in session:
        try:
            amount = float(request.form['amount'])
            type = request.form['type']
            category = request.form['category']
            date = request.form['date']
            description = request.form['description']

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
        except ValueError:
            flash('Invalid amount entered. Please use a valid number.', 'danger')
    return redirect(url_for('index'))

@app.route('/delete_transaction/<int:transaction_id>', methods=['POST'])
def delete_transaction(transaction_id):
    if 'user_id' in session:
        transaction = Transaction.query.get(transaction_id)
        if transaction and transaction.user_id == session['user_id']:
            db.session.delete(transaction)
            db.session.commit()
            flash('Transaction deleted successfully!', 'success')
        else:
            flash('You do not have permission to delete this transaction.', 'danger')
    return redirect(url_for('index'))

@app.route('/edit_transaction/<int:transaction_id>', methods=['POST'])
def edit_transaction(transaction_id):
    if 'user_id' in session:
        transaction = Transaction.query.get(transaction_id)
        if transaction and transaction.user_id == session['user_id']:
            try:
                # Update the transaction with new form data
                transaction.amount = float(request.form['amount'])
                transaction.type = request.form['type']
                transaction.category = request.form['category']
                transaction.date = request.form['date']
                transaction.description = request.form['description']
                db.session.commit()
                flash('Transaction updated successfully!', 'success')
            except ValueError:
                flash('Invalid amount entered. Please use a valid number.', 'danger')
        else:
            flash('You do not have permission to edit this transaction.', 'danger')
    return redirect(url_for('index'))

@app.route('/set_budget', methods=['POST'])
def set_budget():
    if 'user_id' in session:
        user_id = session['user_id']
        category = request.form['category']
        try:
            limit = float(request.form['limit'])
            if limit < 0:
                flash('Budget limit cannot be negative.', 'danger')
                return redirect(url_for('index'))

            # Check if a budget for this category already exists
            budget = Budget.query.filter_by(user_id=user_id, category=category).first()
            if budget:
                budget.limit = limit
                flash(f'Budget for {category} updated to ${limit:.2f}!', 'success')
            else:
                new_budget = Budget(user_id=user_id, category=category, limit=limit)
                db.session.add(new_budget)
                flash(f'New budget for {category} set to ${limit:.2f}!', 'success')

            db.session.commit()
        except ValueError:
            flash('Invalid budget limit entered. Please use a valid number.', 'danger')
    return redirect(url_for('index'))

# Create database tables if they don't exist
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
