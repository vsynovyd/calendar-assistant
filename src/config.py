# config.py

from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OUTLOOK_API_KEY = os.getenv('OUTLOOK_API_KEY')

CLIENT_ID = 'e49f04b4-507b-4e1d-801b-5433c047f53e'
CLIENT_SECRET = 'f23d5e30-8cf8-40e6-938a-df2898ed2927'
TENANT_ID = '6f9b6b26-53a8-4387-b4de-8f8b16e205ee'
REDIRECT_URI = 'http://localhost'