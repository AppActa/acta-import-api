from os import getenv

from dotenv import load_dotenv

load_dotenv()

DB_URL = getenv('DB_URL')

CLOUDINARY_CLOUD_NAME = getenv('CLOUDINARY_CLOUD_NAME')
CLOUDINARY_API_KEY = getenv('CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = getenv('CLOUDINARY_API_SECRET')

ACTA_PG_API_URL = getenv('ACTA_PG_API_URL')

REDIS_HOST = getenv('REDIS_HOST')
REDIS_PORT = getenv('REDIS_PORT')
REDIS_DB = getenv('REDIS_DB')
REDIS_PASSWORD = getenv('REDIS_PASSWORD')
REDIS_SSL = True