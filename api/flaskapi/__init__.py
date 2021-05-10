from flask import Flask
import logging
from logging import Formatter, FileHandler
import os

app = Flask(__name__)

if os.environ['APP_ENVIRONMENT'] == 'development':
    app.config['DEBUG'] = True
    app.config['FLASK_ENV'] = 'development'
else:
    app.config['DEBUG'] = False
    app.config['FLASK_ENV'] = 'production'


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')


from flaskapi import databaseFunctions
from flaskapi import endpoints