import requests
from os.path import join, dirname
from dotenv import load_dotenv
from os import getenv
from pprint import pprint

dotenv_path = join(dirname(__file__), "../.env")
load_dotenv(dotenv_path=dotenv_path)

def login_user(email: str, password: str):
    API_KEY = getenv("API_KEY")
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
    payload = {
        "email": getenv("TESTING_EMAIL", "admin@example.com"),
        "password": getenv("TESTING_PASSWORD", "admin123"),
        "returnSecureToken": True
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json()  # contains idToken, refreshToken, etc
    else:
        raise ValueError("Login failed: " + response.json().get("error", {}).get("message", "Unknown error"))

# Testing.
user_email = getenv("TESTING_USER")
user_password = getenv("TESTING_PASSWORD")
pprint(login_user(email=user_email, password=user_password))
