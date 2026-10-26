# 📚 BookTrack — Book Discovery & Reading Tracker

BookTrack is a web application built with Django that helps users discover books, manage their reading lists, track reading progress, and save favorite books.

## ✨ Features

- 🔍 Search books using the Open Library API
- 📚 Manage personal reading lists
- 📖 Track reading status: Want to Read, Currently Reading, and Completed
- ❤️ Save favorite books
- 📊 View reading statistics on the dashboard
- 🕒 View completed reading history
- 👤 User registration, login, and profile management
- 🔐 Password reset through email
- 🌐 REST API for book search

## 🛠️ Technologies Used

- Python
- Django
- Django REST Framework
- MySQL
- HTML and CSS
- Open Library API

## 🚀 Setup Instructions

1. Clone this repository:

   ```bash
   git clone https://github.com/mohammedshanvc-droid/BookDiscoveryTracker.git
   ```

2. Open the project folder:

   ```bash
   cd BookDiscoveryTracker
   ```

3. Create and activate a virtual environment:

   ```bash
   python -m venv env
   env\Scripts\activate
   ```

4. Install the required packages:

   ```bash
   pip install django djangorestframework mysqlclient python-dotenv Pillow
   ```

5. Create a `.env` file in the project root with your own configuration:

   ```env
   DJANGO_SECRET_KEY=your_secret_key
   DB_PASSWORD=your_mysql_password
   EMAIL_HOST_USER=your_email_address
   EMAIL_HOST_PASSWORD=your_email_app_password
   ```

6. Create a MySQL database named `book_tracker` and configure your database settings.

7. Apply migrations:

   ```bash
   python manage.py migrate
   ```

8. Start the development server:

   ```bash
   python manage.py runserver
   ```

9. Open `http://127.0.0.1:8000/` in your browser.

## 🔒 Security

Never upload your `.env` file, passwords, or secret keys to GitHub.

## 👨‍💻 Developer

**Mohammed Shan V C**

GitHub: [mohammedshanvc-droid](https://github.com/mohammedshanvc-droid)

---

*Discover books. Track your reading. Find your next story.*
