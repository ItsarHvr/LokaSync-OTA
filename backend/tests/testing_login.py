import requests
from os.path import join, dirname
from dotenv import load_dotenv
from os import getenv
from pprint import pprint

dotenv_path = join(dirname(__file__), "../.env")
load_dotenv(dotenv_path=dotenv_path)

API_KEY = getenv("API_KEY")
EMAIL = getenv("TESTING_LOGIN_EMAIL")
PASSWORD = getenv("TESTING_LOGIN_PASSWORD")

def login_user(email: str, password: str):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json()  # contains idToken, refreshToken, etc
    else:
        raise ValueError("Login failed: " + response.json().get("error", {}).get("message", "Unknown error"))

# Testing.
pprint(
    login_user(EMAIL, PASSWORD)
)
