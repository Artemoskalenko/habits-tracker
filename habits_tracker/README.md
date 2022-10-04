# Habit tracker django application that helps you to build good habits, reach your goals
## To run application on local machine:
#### 1. Clone the repository:
`git clone https://github.com/Artemoskalenko/habits-tracker.git && cd habits-tracker && cd habits_tracker`
#### 2. Create a virtual environment:
`python3 -m venv venv`
#### 3. Activate the virtual environment:
`source venv/bin/activate`
#### 4. Install all required dependencies:
`pip install -r requirements.txt`
#### 5. Collect static files:
`python manage.py collectstatic`
#### 6. Apply the migrations:
`python manage.py migrate`
#### 7. Create superuser:
`python manage.py createsuperuser`
#### 8. Run server:
`python manage.py runserver`
#### 9. From now local version is available at http://localhost:8000
