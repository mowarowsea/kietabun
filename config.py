import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")
DATABASE_API_KEY = os.environ.get("DATABASE_API_KEY")
