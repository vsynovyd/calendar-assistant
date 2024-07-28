"""
calendar_integration.py

Integrates with the Outlook calendar API for authentication and fetching events.
"""

import requests
import msal
from config import CLIENT_ID, CLIENT_SECRET, TENANT_ID, REDIRECT_URI

class OutlookCalendar:
    """
    Outlook Calendar integration.

    Attributes:
    ----------
    client_id : str
    client_secret : str
    tenant_id : str
    app : msal.ConfidentialClientApplication
    token : dict

    Methods:
    -------
    initialize_msal_app()
    authenticate()
    get_access_token()
    get_events()
    get_calendar_events(start_date, end_date)
    """

    def __init__(self, client_id, client_secret, tenant_id):
        """
        Initializes OutlookCalendar with client ID, client secret, and tenant ID.
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.app = self.initialize_msal_app()
        self.token = self.authenticate()

    def initialize_msal_app(self):
        """
        Initializes the MSAL application.
        """
        authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        return msal.ConfidentialClientApplication(
            self.client_id, authority=authority, client_credential=self.client_secret
        )

    def authenticate(self):
        """
        Authenticates and acquires a token.
        """
        token = self.app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
        if "access_token" in token:
            return token
        else:
            raise Exception("Could not acquire token: " + token.get("error_description", "Unknown error"))

    def get_access_token(self):
        """
        Retrieves a valid access token.
        """
        result = self.app.acquire_token_silent(scopes=["https://graph.microsoft.com/.default"], account=None)
        if not result:
            result = self.app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
        return result['access_token']

    def get_events(self):
        """
        Fetches all events from the user's calendar.
        """
        headers = {"Authorization": f"Bearer {self.token['access_token']}"}
        response = requests.get("https://graph.microsoft.com/v1.0/me/events", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error fetching events: {response.status_code} - {response.text}")

    def get_calendar_events(self, start_date, end_date):
        """
        Fetches calendar events within a specified date range.
        """
        token = self.get_access_token()
        endpoint = "https://graph.microsoft.com/v1.0/me/calendarview"
        headers = {"Authorization": f"Bearer {token}"}
        params = {
            "startDateTime": start_date.isoformat(),
            "endDateTime": end_date.isoformat()
        }
        response = requests.get(endpoint, headers=headers, params=params)
        if response.status_code == 200:
            return response.json().get('value', [])
        else:
            raise Exception(f"Error fetching calendar events: {response.status_code} - {response.text}")

