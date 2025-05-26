from firebase_admin import _apps, credentials, initialize_app
from os.path import join, dirname

from cores.config import env

# cert = Path(__file__).resolve().parent.parent.parent / env.FIREBASE_CREDS_NAME
FIREBASE_CREDS_PATH = join(dirname(__file__), "../../../", env.FIREBASE_CREDS_NAME)

def init_firebase_app() -> bool:
    """
    Initialize Firebase app with the given credentials.
    """
    try:
        with open(FIREBASE_CREDS_PATH, 'r'):
            print(f"✅ Firebase credentials file found")
    except FileNotFoundError:
        print(f"❌ Firebase credentials file not found")
        return False

    if not _apps:
        creds = credentials.Certificate(FIREBASE_CREDS_PATH)
        initialize_app(creds)
        print("✅ Firebase app initialized successfully.")
    else:
        print("❌ Firebase app already initialized, skipping re-initialization.")
    
    return True