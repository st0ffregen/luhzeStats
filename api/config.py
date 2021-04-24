import os

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enables debug mode depending on run level
if os.environ['APP_ENVIRONMENT'] == 'development':
    DEBUG = True
else:
    DEBUG = False

APPLICATION_ROOT = '/api'
