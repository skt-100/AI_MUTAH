import os

# Data Base
DB_HOST     = "localhost"
DB_USER     = ""
DB_PASSWORD = ""
DB_NAME     = ""
DB_PORT     = 3306
DB_CHARSET  = "utf8mb4"

DB_CONFIG = {
  "host":     DB_HOST,
  "user":     DB_USER,
  "password": DB_PASSWORD,
  "database": DB_NAME,
  "port":     DB_PORT,
  "charset":  DB_CHARSET,
}

# Flask
FLASK_HOST  = "0.0.0.0"
FLASK_PORT  = 5000
FLASK_DEBUG = True
SECRET_KEY  = "mutah_it_secret_2026"

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR  = os.path.join(BASE_DIR, "..", "Web")
IT_DIR   = os.path.join(WEB_DIR, "Information_Technology")
HTML_DIR = os.path.join(IT_DIR, "HTML")


