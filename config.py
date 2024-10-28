from os import environ
from dotenv import load_dotenv

load_dotenv()

USERNAME = environ.get('USERNAME')
PASSWORD = environ.get('PASSWORD')