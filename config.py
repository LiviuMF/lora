from os import environ
from dotenv import load_dotenv

load_dotenv()

USERNAME = environ.get('USERNAME')
PASSWORD = environ.get('PASSWORD')
TO_EMAIL = 'liviu.m.farcas@gmail.com'
FROM_EMAIL = 'office@cohe.ro'
EMAIL_HOST = environ.get('EMAIL_HOST')
EMAIL_PORT = environ.get('EMAIL_PORT')
EMAIL_USERNAME = environ.get('EMAIL_USERNAME')
EMAIL_PASSWORD = environ.get('EMAIL_PASSWORD')
ALLOWED_ATTACHMENT_TYPES = ['pdf', 'png', 'jpg', 'jpeg']
