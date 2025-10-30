#  Fit Life – Backend

## Project Overview
**Fit Life** is a fitness web application that helps users improve their lifestyle by providing personalized workout plans and tracking their daily progress.  
The backend is built with **Django REST Framework** and provides the main API for managing users, profiles, workouts, and progress data.

---

## Technologies Used
- **Python 3**
- **Django**
- **Django REST Framework**
- **SQLite (development database)**

---

##  Project Structure
``
backend-fitlife/
│
├── backend/ # Django project (settings, urls, wsgi, asgi)
├── main_app/ # Main app (core backend logic)
│ ├── models.py
│ ├── views.py
│ ├── urls.py
│ └── serializers.py
│
├── manage.py # Django management commands
├── Pipfile # Dependencies for pipenv
└── db.sqlite3 # Local development database
``

---
