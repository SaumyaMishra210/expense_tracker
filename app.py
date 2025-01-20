from flask import Flask,render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from models.expenses import Expense
from models import db
from flask import flash
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'  # Path to the database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking

# Set the secret key from an environment variable
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_secret_key')

# Initialize db with the app
db.init_app(app)


@app.route('/', endpoint='index')
def index():
    # Get the sorting criteria from the user, default is 'date'
    sort_by = request.args.get('sort_by', 'date')  # Default to sorting by date
    order = request.args.get('order', 'asc')  # Default to ascending order

    # Define the sorting fields (you can extend this list if needed)
    sorting_fields = {
        'date': Expense.date,
        'amount': Expense.amount,
        'category': Expense.category
    }

    # Determine the sort order
    sort_field = sorting_fields.get(sort_by, Expense.date)
    if order == 'desc':
        expenses = Expense.query.order_by(sort_field.desc()).all()
    else:
        expenses = Expense.query.order_by(sort_field.asc()).all()

    # Calculate the total expenses
    total_expenses = sum(expense.amount for expense in expenses)

    return render_template('index.html', expenses=expenses, total_expenses=total_expenses, sort_by=sort_by, order=order)



@app.route('/add_expenses', methods=['GET', 'POST'])
def add_expenses():
    if request.method == 'POST':
        # Your code for handling form submission
        date = request.form.get('date')
        amounts = request.form.getlist('amount[]')
        categories = request.form.getlist('category[]')

        # Process the data (e.g., save it to the database)
        for amount, category in zip(amounts, categories):
            # Save the record to the database
            new_expense = Expense(date=date, amount=amount, category=category)
            db.session.add(new_expense)
        
        db.session.commit()

        flash("Expenses added successfully!", "success")
        return redirect(url_for('add_expenses'))
    
    return render_template('add_expenses.html')  # Render the form for GET request




@app.route('/visualize')
def visualize():
    # Query the database for expenses grouped by category
    expenses = db.session.query(
        Expense.category, 
        db.func.sum(Expense.amount).label('total')
    ).group_by(Expense.category).all()

    # Prepare data for the chart
    labels = [expense.category for expense in expenses]
    values = [expense.total for expense in expenses]

    return render_template('visualize.html', labels=labels, values=values)

@app.route('/delete_expense/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    db.session.delete(expense)
    db.session.commit()

    flash('Expense deleted successfully!', 'success')  # Flash message
    return redirect(url_for('index'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables
    app.run(debug=True)