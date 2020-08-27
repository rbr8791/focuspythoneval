from os import environ
from sys import exit

# import ptvsd
from flask_migrate import Migrate
from flask_seeder import FlaskSeeder

from app import create_app, db
from config import config_dict

get_config_mode = environ.get('ITUNES_API_PROCESSOR_CONFIG_MODE', 'Debug')

try:
    ENV = ''
    # with open('sysenv.env', 'r') as myenv:
    #     try:
    #         ENV = myenv.read()
    #         if ENV == "PROD":
    #             SYSTEM_ENV = "production"
    #         elif ENV == "TEST":
    #             SYSTEM_ENV = "test"
    #     except Exception as ex:
    #         ENV = "TEST"
    #         SYSTEM_ENV = "test"
    ENV = "TEST"
    SYSTEM_ENV = "test"
    config_mode = config_dict[get_config_mode.capitalize()]
except KeyError:
    exit('Error: Invalid ITUNES_API_PROCESSOR_CONFIG_MODE environment variable entry.')

app = create_app(config_mode)
# seeder.seed_database(app, db)
seeder = FlaskSeeder()
seeder.init_app(app, db)
Migrate(app, db)
