import os

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enables debug mode depending on run level
if os.environ['APP_ENVIRONMENT'] == 'development':
    DEBUG = True
    FLASK_ENV = 'development'
else:
    DEBUG = False
    FLASK_ENV = 'production'

APPLICATION_ROOT = '/api'
