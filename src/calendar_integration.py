"""
calendar_integration.py

This module is responsible for integrating with the calendar API. It handles 
authentication and fetching calendar events
"""

import requests
import msal
from config import CLIENT_ID, CLIENT_SECRET, TENANT_ID, REDIRECT_URI

class OutlookCalendar:
    def __init__(self, client_id, client_secret, tenant_id):
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.token = self.authenticate()

    def authenticate(self):
        authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        app = msal.ConfidentialClientApplication(
            self.client_id, authority=authority, client_credential=self.client_secret
        )
        token = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
        if "access_token" in token:
            return token
        else:
            raise Exception("Could not acquire token: " + token.get("error_description", "Unknown error"))

    def get_events(self):
        headers = {"Authorization": f"Bearer {self.token['access_token']}"}
        response = requests.get("https://graph.microsoft.com/v1.0/me/events", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error fetching events: {response.status_code} - {response.text}")

if __name__ == "__main__":
    calendar = OutlookCalendar(CLIENT_ID, CLIENT_SECRET, TENANT_ID)
    events = calendar.get_events()
    print(events)