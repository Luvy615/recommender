import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "fashion_assistant")

    DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")

    USE_SQLITE = os.getenv("USE_SQLITE", "true").lower() == "true"

    if USE_SQLITE:
        DATABASE_URL = "sqlite:///./fashion_assistant.db"
    else:
        DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"


config = Config()
