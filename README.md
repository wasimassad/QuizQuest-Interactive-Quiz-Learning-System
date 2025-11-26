# QuizQuest - Interactive Quiz Learning System

A web-based interactive quiz platform built with Django and MySQL, featuring authentication, RBAC, CRUD question management, audit logging, file attachments, and secure database design.

## Features

- **User Authentication**: Login, registration, and logout functionality
- **Role-Based Access Control (RBAC)**: Admin and Standard user roles
- **Quiz Questions CRUD**: Create, read, update, and delete quiz questions (admin only)
- **Audit Logging**: Track user actions including login, logout, and CRUD operations
- **File Upload Support**: Profile pictures and question images
- **Admin Dashboard**: Overview of users, questions, and recent activity

## Requirements

- Python 3.10+
- MySQL 8.0+ (or SQLite for development)
- pip

## Installation

1. Clone the repository:
```bash
git clone https://github.com/wasimassad/QuizQuest-Interactive-Quiz-Learning-System.git
cd QuizQuest-Interactive-Quiz-Learning-System
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

5. Configure your database settings in `.env`:
```
# For MySQL
DB_ENGINE=mysql
DB_NAME=quizquest
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306

# For SQLite (development)
DB_ENGINE=sqlite
```

6. Run migrations:
```bash
python manage.py migrate
```

7. Create a superuser:
```bash
python manage.py createsuperuser
```

8. Run the development server:
```bash
python manage.py runserver
```

9. Visit `http://localhost:8000` in your browser.

## Project Structure

```
QuizQuest/
├── manage.py
├── requirements.txt
├── .env.example
├── quizquest/           # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── quiz/                # Main app
│   ├── models.py        # User, Role, Question, AuditLog models
│   ├── views.py         # View functions
│   ├── forms.py         # Form classes
│   ├── urls.py          # URL patterns
│   ├── admin.py         # Admin configuration
│   └── tests.py         # Test cases
├── templates/           # HTML templates
│   ├── base.html
│   └── quiz/
│       ├── home.html
│       ├── login.html
│       ├── register.html
│       ├── admin_dashboard.html
│       └── question_*.html
├── static/              # Static files
│   ├── css/
│   └── js/
└── media/               # Uploaded files
```

## Running Tests

```bash
DB_ENGINE=sqlite python manage.py test quiz
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DJANGO_SECRET_KEY` | Django secret key | Auto-generated |
| `DJANGO_DEBUG` | Debug mode | `True` |
| `DJANGO_ALLOWED_HOSTS` | Allowed hosts | `localhost,127.0.0.1` |
| `DB_ENGINE` | Database engine (`mysql` or `sqlite`) | `mysql` |
| `DB_NAME` | Database name | `quizquest` |
| `DB_USER` | Database user | `root` |
| `DB_PASSWORD` | Database password | (empty) |
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `3306` |

## License

MIT License
