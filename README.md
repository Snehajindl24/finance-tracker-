# An Open-Source Finance Tracker

Tired of complicated spreadsheets and subscription fees? This project is a simple, yet powerful, personal finance tracker built to help you take control of your money with a clean, intuitive interface. Designed for simplicity and insight, it's the perfect tool to visualize your spending and work towards your financial goals.

✨ Motivation
The world of personal finance can feel overwhelming. Many of us want to track our spending, but the tools available are often too complex, expensive, or lack a clear focus. The goal of this project is to provide a straightforward, open-source alternative. By building this with a focus on ease-of-use and clear data visualization, we can make financial tracking accessible to everyone. This is a community-driven project, and your contributions and ideas are what will make it better.

📈 Features
🔒 Secure Authentication: A robust and secure system for user registration and login, ensuring your financial data is safe.

📝 Effortless Transaction Logging: Quickly and easily add, edit, and delete transactions for both income and expenses.

📊 At-a-Glance Dashboard: A centralized dashboard provides a real-time summary of your total income, total expenses, and current net balance.

💰 Smart Monthly Budgeting: Set and monitor spending limits for different categories with a visual progress bar and automatic warnings when you're close to or over budget.

📉 Powerful Data Visualization: Understand your spending habits at a glance with interactive doughnut and bar charts that break down your finances by category.

🌙 Dark Mode: A toggle for a comfortable, eye-friendly dark mode experience.

📸 App Preview
Here is a look at the application's main dashboard in action, showcasing the key features.

💻 Tech Stack
This application is built with a simple but effective stack that prioritizes speed and maintainability.

Backend:

Flask: Chosen for its lightweight nature, making it ideal for rapid development and simple, scalable web applications.

Flask-SQLAlchemy: A powerful tool for interacting with the database without writing raw SQL.

Werkzeug: The underlying toolkit that provides the core functionalities of the web application.

SQLite: A simple, file-based database for local development, making it easy to set up and run without external database servers.

Frontend:

HTML & CSS: The foundation of the user interface, with a custom responsive design and theming for a polished look.

JavaScript: Powers the dynamic features like charts, modals, and the dark mode toggle.

Chart.js: An elegant and easy-to-use library for creating beautiful and informative charts from your financial data.

Font Awesome: Provides a lightweight set of vector icons to enhance the user interface.

⚙️ Setup and Installation
Follow these steps to get a local copy of the project up and running.

Prerequisites
Python 3.8+

pip (Python package installer)

Installation
Clone the repository:

git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name

Create and activate a virtual environment:

python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS and Linux:
source venv/bin/activate

Install the required packages:

pip install -r requirements.txt

Run the application:

flask run

The application should now be running at http://127.0.0.1:5000.

🚀 Roadmap
This project is a work in progress, and there are many exciting features on the horizon. Some ideas include:

Recurring Transactions: The ability to automatically add transactions that happen regularly.

More Advanced Reporting: Generate monthly or yearly reports on spending habits.

User Profile Settings: Customize preferences and manage account details.

Export Data: Option to export financial data to a CSV file.

Feel free to suggest new ideas or pick up a task from the roadmap!
