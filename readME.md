# Guiana Chestnut
<p style="text-align: center">Web application built for analysing financial instruments and personal trading.</p>

### Todo
- [] Prevent access to login & register page when logged in
- [] Prevent access to login-only pages when not logged in

### Debugging
Sync database after making migrations:
```python manage.py migrate --run-syncdb```

### Unit Testing
Run unit tests
```coverage run manage.py test```

Create coverage report
```coverage html```