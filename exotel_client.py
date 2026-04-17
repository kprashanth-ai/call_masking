import os
import requests
from dotenv import load_dotenv

load_dotenv()

ACCOUNT_SID = os.getenv("EXOTEL_ACCOUNT_SID")
API_KEY = os.getenv("EXOTEL_API_KEY")
API_TOKEN = os.getenv("EXOTEL_API_TOKEN")
VIRTUAL_NUMBER = os.getenv("EXOTEL_VIRTUAL_NUMBER")

BASE_URL = f"https://api.exotel.com/v1/Accounts/{ACCOUNT_SID}"
AUTH = (API_KEY, API_TOKEN)


def bridge_call(patient_phone: str, paramedic_phone: str, status_callback: str = "") -> dict:
    """
    Exotel dials patient_phone first; when answered, bridges to paramedic_phone.
    Paramedic sees VIRTUAL_NUMBER as caller ID — never the patient's real number.
    """
    payload = {
        "From": patient_phone,
        "To": paramedic_phone,
        "CallerId": VIRTUAL_NUMBER,
        "Record": "true",
    }
    if status_callback:
        payload["StatusCallback"] = status_callback

    resp = requests.post(f"{BASE_URL}/Calls/connect.json", auth=AUTH, data=payload)
    resp.raise_for_status()
    return resp.json()


def get_call(call_sid: str) -> dict:
    resp = requests.get(f"{BASE_URL}/Calls/{call_sid}.json", auth=AUTH)
    resp.raise_for_status()
    return resp.json()


def verify_credentials() -> bool:
    """Ping the account endpoint to confirm credentials are valid."""
    try:
        resp = requests.get(f"{BASE_URL}.json", auth=AUTH, timeout=5)
        return resp.status_code == 200
    except requests.RequestException:
        return False
