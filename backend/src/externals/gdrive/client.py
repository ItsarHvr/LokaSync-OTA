from os.path import join, dirname

from cores.config import env

# SERVICE_ACCOUNT_FILE = Path(__file__).resolve().parent.parent.parent / env.GOOGLE_DRIVE_CREDS_NAME
SERVICE_ACCOUNT_FILE = join(dirname(__file__), "../../../", env.GOOGLE_DRIVE_CREDS_NAME)
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def check_google_drive_credentials() -> bool:
    """
    Check if the Google Drive credentials file exists.
    """
    try:
        with open(SERVICE_ACCOUNT_FILE, 'r'):
            print("✅ Google Drive credentials file found.")
        return True
    except FileNotFoundError:
        print(f"❌ Google Drive credentials file not found: {SERVICE_ACCOUNT_FILE}")
        return False