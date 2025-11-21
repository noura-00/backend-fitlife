# Migration Instructions

## Run these commands to apply the database changes:

```bash
cd backend-fitlife
pipenv run python manage.py makemigrations main_app
pipenv run python manage.py migrate
```

## Expected Migration

The migration will:
- Add `age` field (IntegerField, null=True, blank=True)
- Add `show_age_public` field (BooleanField, default=False)
- Add `show_height_public` field (BooleanField, default=False)
- Change `height` from FloatField to IntegerField (with null=True, blank=True)

## After Migration

All existing profiles will have:
- `age` = None
- `height` = None (or existing value converted to int)
- `show_age_public` = False
- `show_height_public` = False

No data will be lost.





