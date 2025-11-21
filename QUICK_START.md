# Quick Start Guide - Fix 500 Error

## Step 1: Make sure Backend is running

Open a terminal and run:

```bash
cd backend-fitlife
python3 manage.py runserver
```

You should see:
```
Starting development server at http://127.0.0.1:8000/
```

## Step 2: If you see database errors, run migrations:

```bash
cd backend-fitlife
python3 manage.py migrate
```

## Step 3: Check if the server is accessible

Open browser and go to: `http://localhost:8000`

You should see: `{"message": "Welcome to the FitLife api home route!"}`

## Step 4: Check Backend console for error details

When you try to login/signup, check the terminal where `runserver` is running. 
You will see detailed error messages there.

## Common Issues:

### Issue: "ModuleNotFoundError: No module named 'django'"
**Solution**: Install dependencies:
```bash
cd backend-fitlife
pip3 install -r requirements.txt
```

Or if using Pipenv:
```bash
pipenv install
pipenv shell
```

### Issue: Database not found
**Solution**: Run migrations:
```bash
python3 manage.py migrate
```

### Issue: Still getting 500 error
**Solution**: Check the terminal output for the exact error message and share it.











