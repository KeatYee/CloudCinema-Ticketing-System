import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_key_very_secret'
    DB_HOST = os.environ.get('DB_HOST') or 'localhost'
    DB_USER = os.environ.get('DB_USER') or 'root'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or 'password'
    DB_NAME = os.environ.get('DB_NAME') or 'moviedb'