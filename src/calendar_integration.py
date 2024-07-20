"""
calendar_integration.py

This module is responsible for integrating with the calendar API. It handles 
authentication and fetching calendar events
"""

import requests
import msal
from config import CLIENT_ID, CLIENT_SECRET, TENANT_ID, REDIRECT_URI

def get_msal_app():
    """Initialize the MSAL Confidential Client Application."""
    return msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}",
        client_credential=CLIENT_SECRET,
    )

def get_access_token():
    """Acquire a token from Azure AD."""
    app = get_msal_app()
    result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    
    if "access_token" in result:
        return result["access_token"]
    else:
        raise Exception("Could not acquire token: " + result.get("error_description", "Unknown error"))

def get_calendar_events(access_token):
    """Fetch calendar events using the Microsoft Graph API."""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    response = requests.get(
        "https://graph.microsoft.com/v1.0/me/events",
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error fetching events: {response.status_code} - {response.text}")

if __name__ == "__main__":
    token = get_access_token()
    events = get_calendar_events(token)
    print(events)