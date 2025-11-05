# FitLife - Backend API

## Project Overview

**FitLife** is a fitness web application that helps users improve their lifestyle by providing personalized workout plans and tracking their daily progress.  
The backend is built using **Django REST Framework** and provides the main API for managing users, profiles, workouts, and data.

---



## Technologies Used

- **Python 3.13**
- **Django 5.2.7**
- **Django REST Framework**
- **Django REST Framework Simple JWT** (for authentication)
- **Pillow** (for image processing)
- **django-cors-headers** (for CORS management)
- **python-dotenv** (for environment variables management)
- **SQLite** (development database)
- **Pipenv** (package management)

---

## Project Structure

```
backend-fitlife/
│
├── backend/                    # Main Django project
│   ├── settings.py            # Project settings
│   ├── urls.py                # Main project URLs
│   ├── wsgi.py                # WSGI configuration
│   └── asgi.py                # ASGI configuration
│
├── main_app/                   # Main application
│   ├── models.py              # Database models
│   ├── views.py               # Views (data presentation)
│   ├── urls.py                # Application URLs
│   ├── serializers.py         # Data serializers
│   ├── admin.py               # Django Admin settings
│   ├── management/
│   │   └── commands/
│   │       └── seed_workout_plans.py  # Command to seed workout data
│   └── migrations/            # Database migration files
│
├── media/                      # User uploads
│   ├── profile_pics/          # Profile pictures
│   └── post_images/           # Post images
│
├── manage.py                   # Django management commands
├── Pipfile                     # Pipenv dependencies file
├── Pipfile.lock               # Package version lock
├── db.sqlite3                  # Local database
└── README.md                   # This file
```

---

## ERD
![ERD Diagram](./images/erd-diagram.png)


## Models

### 1. UserProfile
- **user**: One-to-one relationship with Django User
- **height**: Height
- **current_weight**: Current weight
- **target_weight**: Target weight
- **goal**: Goal
- **activity_level**: Activity level
- **profile_picture**: Profile picture
- **bio**: Biography
- **followers_count**: Number of followers
- **following_count**: Number of following
- **selected_workout_plan**: Selected workout plan

### 2. WorkoutPlan
- **user**: Owner user (optional)
- **title**: Plan title
- **goal_type**: Goal type (cut, bulk, maintain, home)
- **equipment_needed**: Required equipment
- **duration**: Duration in weeks
- **description**: Description
- **notes**: Notes
- **created_at**: Creation date

### 3. Post
- **user**: Creator user
- **workout_plan**: Associated workout plan (optional)
- **content**: Post content
- **image**: Post image (optional)
- **created_at**: Creation date

### 4. Comment
- **post**: Associated post
- **user**: User who added the comment
- **content**: Comment content
- **created_at**: Creation date

---

## API Endpoints

### Authentication & Users
- `GET /` - API home page
- `POST /users/signup/` - Create new account
- `POST /users/login/` - Login
- `GET /users/profile/` - Get user profile
- `PUT /users/profile/` - Update user profile
- `DELETE /users/profile/` - Delete user profile

### Workout Plans
- `GET /workouts/` - List all workout plans
- `POST /workouts/` - Create new workout plan
- `GET /workouts/<id>/` - Get specific workout plan
- `PUT /workouts/<id>/` - Update workout plan
- `DELETE /workouts/<id>/` - Delete workout plan

### Posts
- `GET /posts/` - List all posts
- `POST /posts/` - Create new post
- `GET /posts/<id>/` - Get specific post
- `PUT /posts/<id>/` - Update post
- `DELETE /posts/<id>/` - Delete post

### Comments
- `GET /posts/<post_id>/comments/` - List post comments
- `POST /posts/<post_id>/comments/` - Add new comment
- `GET /comments/<id>/` - Get specific comment
- `PUT /comments/<id>/` - Update comment
- `DELETE /comments/<id>/` - Delete comment

---

## Setup Instructions

### 1. Install Python and Pipenv
```bash
# Verify Python 3.13 is installed
python3 --version

# Install Pipenv if not installed
pip install pipenv
```

### 2. Clone Project and Install Dependencies
```bash
# Navigate to project directory
cd backend-fitlife

# Install dependencies
pipenv install

# Activate virtual environment
pipenv shell
```

### 3. Setup Environment File (.env)
Create a `.env` file in the `backend-fitlife` directory and add:
```env
SECRET_KEY=your-secret-key-here
```

### 4. Run Migrations
```bash
# Create migration files
python manage.py makemigrations

# Apply migrations to database
python manage.py migrate
```

### 5. Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### 6. Seed Workout Data (Optional)
```bash
python manage.py seed_workout_plans
```

### 7. Run Server
```bash
python manage.py runserver
```

The server will run on `http://127.0.0.1:8000`

---

## CORS Configuration

CORS is configured to allow requests from:
- `http://localhost:5174`
- `http://127.0.0.1:5174`

You can modify `CORS_ALLOWED_ORIGINS` in `backend/settings.py`

---

## Static Files and Media Serving

In development environment, static files and media are automatically served through `backend/urls.py`

---

## Authentication

The project uses **JWT (JSON Web Tokens)** for authentication:
- Upon login, an access token is returned
- The token must be included in request header: `Authorization: Bearer <token>`
- Token expiration: 60 minutes (configurable)

---

## Testing

```bash
# Run tests
python manage.py test
```

---

## Common Issues

### Issue: ModuleNotFoundError: No module named 'dotenv'
**Solution**: Install `python-dotenv`:
```bash
pipenv install python-dotenv
```

### Issue: CORS Policy Error
**Solution**: Make sure to add the frontend URL to `CORS_ALLOWED_ORIGINS` in `backend/settings.py`

### Issue: Images Not Showing
**Solution**: Make sure to add the media serving line in `backend/urls.py`:
```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

## Contributing

1. Fork the project
2. Create a new branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## License

This project is open source and available for use.

---

## Contact

For help or inquiries, please open an issue in the repository.
